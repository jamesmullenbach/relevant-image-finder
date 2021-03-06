# The "main" file
# This file handles incoming HTTP requests.
import os
import sys, errno
from flask import Flask, request, jsonify
import er
import requests
import nltk
import string
import lxml
import unicodedata
from lxml.html.clean import Cleaner
import dehtml

from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)
#limit the number of results to return
NUM_RESULTS = 10

@app.route('/')
def main():
	# main method - takes in a bunch of text, returns list of img urls
	# create response object
	response = {
		"results": []
	}

	try:
		#first get the text from the request
		text = request.args.get('text', '')

		#create translation table to remove punctuation
		translation = {ord(c) : None for c in string.punctuation}
		noPunct = text.translate(translation)

		#make it ascii
		ascii = unicodedata.normalize("NFKD", noPunct).encode("ascii", "ignore")

		# Entity Recognizer component. Contained in the file er.py.
		ents = er.getEntities(ascii)
		if ents:
			# Image Search component.
			#	searches for: first 3 entities recognized
			#	search for the images on google, and also do face detection if necessary
			faceSrcs, noFaceSrcs, faceUrls, noFaceUrls = imageSearch(ents[:min(len(ents),3)])

			# Post-processing/Custom Results Ranker component.
			# do tfidf
			sortedSrcs = tfidfScores(faceUrls, noFaceUrls, faceSrcs, noFaceSrcs, ascii)

			# Append the result to the response
			entityResponse = ents[0][0]
			for i in range(1, min(len(ents),4)):
				entityResponse += " and " + ents[i][0]
			response["results"].append({
				"entity": entityResponse,
				"urls": sortedSrcs
			})

	except IOError as e:
		if e.errno == errno.EPIPE:
			pass
		else:
			raise e
	#return the json
	return jsonify(response)


def imageSearch(entities):

	#check if we should do face detection
	doFaceDetection = False
	for (string, label) in entities:
		if label == u"PERSON":
			#only do it for three-entity searches because of api limits
			if len(entities) > 2:
				doFaceDetection = True

	#build query string with proper quotes
	queryString = ""
	for i in range(len(entities)):
		queryString += '"'
		queryString += entities[i][0].replace(' ', '+')
		queryString += '"'
		if i < len(entities) - 1:
			queryString += '+'

	print("queryString: " + queryString)

	# Dummy account
	r = requests.get('https://www.googleapis.com/customsearch/v1?key=dummyKey&cx=foo:bar&q=' + queryString)

	#turn json into a python dictionary
	responseDict = r.json()
	snippets = []
	srcs = []
	urls = []

	#gather image source and url from google api response
	if "items" in responseDict:
		items = responseDict["items"]

		for i in range(NUM_RESULTS):
			if len(items) > i:
				snippet = items[i]["snippet"]
				try:
					src = items[i]["pagemap"]['cse_image'][0]['src']
				except KeyError:
					try:
						src = items[i]["pagemap"]["imageobject"][0]['url']
					except KeyError:
						src = "n/a"
				url = items[i]["formattedUrl"]
				#collect only proper http urls
				if not (url[0:7] == "http://" or url[0:8] == "https://"):
					url = "http://" + url

				print(url)
				snippets.append(snippet)
				srcs.append(src)
				urls.append(url)

	if doFaceDetection:
		print "doing face detection..."
		faces = []
		for i in range(len(srcs)):
			#api call to Kairos
			headers = {"app_id": "dummyId", "app_key":"dummyKey", "Content-Type": "application/json"}
			payload = {"image": srcs[i]}
			r = requests.post("https://api.kairos.com/detect", headers=headers, json=payload)
			if r.status_code == 200:
				if r.text != '':
					responseDict = r.json()
					if "Errors" in responseDict.keys():
						faces.append(False)
					else:
						#successfully detected a face
						faces.append(True)
				else:
					faces.append(False)
			else:
				faces.append(False)
		print "done with face detection"

		#split image sources and urls into those with faces and those without
		faceSrcs = []
		noFaceSrcs = []
		faceUrls = []
		noFaceUrls = []
		for i in range(len(faces)):
			if faces[i] == True:
				faceSrcs.append(srcs[i])
				faceUrls.append(urls[i])
			elif faces[i] == False:
				noFaceSrcs.append(srcs[i])
				noFaceUrls.append(urls[i])
		# return face-detected images first, they are given priority
		return (faceSrcs, noFaceSrcs, faceUrls, noFaceUrls)

	#if didn't do face detection, just put None for the face objects
	return (None, srcs, None, urls)

#used in tfidf
def tokenize(text):
	return nltk.word_tokenize(text)

#return a list of (image) source urls, ranked by tf-idf of the corresponding webpage
def tfidfScores(faceUrls, noFaceUrls, faceSrcs, noFaceSrcs, sourceContent):
	print "srcs: " + str(noFaceSrcs)
	print "getting tfidf scores"
	sortedSrcs = []
	if faceUrls is not None and faceSrcs is not None:
		faceDocuments = []
		for i in range(len(faceUrls)):
			try:
				# get html from search result url
				response = requests.get(faceUrls[i])

				#don't consider url if we don't get a good response
				if response.status_code == 200 and response.text != '':
					#try to decode
					encoding = response.encoding
					text = response.content.decode(encoding)

					#clean the javascript and css from the html file
					cleaner = Cleaner()
					cleaner.javascript = True
					cleaner.style = True

					cleaned = cleaner.clean_html(text)

					#try to extract only the text from the remaining html
					try:
						parsed = (dehtml.dehtml(cleaned))
					except UnicodeDecodeError:
						print "UnicodeDecodeError"
						# discard this url
						continue

					#lowercase it and remove punctuation
					lowers = parsed.lower()
					if type(lowers) is unicode:
						ascii = unicodedata.normalize("NFKD", lowers).encode("ascii", "ignore")
						noPunct = ascii.translate(None, string.punctuation)
					elif type(lowers) is str:
						noPunct = lowers.translate(None, string.punctuation)
					faceDocuments.append(noPunct)
			except:
				pass

		#lowercase the source content (which has already had punctuation removed)
		lowers = sourceContent.lower()
		faceDocuments.insert(0, lowers)

		#tfidf on the documents (search results along with source content)
		tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words="english")
		faceTfs = tfidf.fit_transform(faceDocuments)

		#cosine similarity
		faceSimilarity = faceTfs * faceTfs.T

		#convert 0th row into an array (document similarities to the source content)
		similarities = []
		print("building similarities")
		print("face similarity length: %d" % faceSimilarity.get_shape()[1])
		for i in range(faceSimilarity.get_shape()[1]):
			similarities.append(faceSimilarity[0,i])

		#sort the sources by decreasing cosine similarity
		indices = [i[0] for i in sorted(enumerate(similarities), key=lambda x:x[1], reverse=True)]

		for i in range(len(indices)):
			if len(faceSrcs) > indices[i]:
				sortedSrcs.append(faceSrcs[indices[i]])

	#same as above but for no-face-detection urls
	noFaceDocuments = []
	for i in range(len(noFaceUrls)):
		try:
			response = requests.get(noFaceUrls[i])

			if response.status_code == 200 and response.text != '':
				encoding = response.encoding
				text = response.content.decode(encoding)

				cleaner = Cleaner()
				cleaner.javascript = True
				cleaner.style = True

				cleaned = cleaner.clean_html(response.content)

				try:
					parsed = (dehtml.dehtml(cleaned))
				except UnicodeDecodeError:
					print "UnicodeDecodeError"
					continue

				lowers = parsed.lower()
				if type(lowers) is unicode:
					ascii = unicodedata.normalize("NFKD", lowers).encode("ascii", "ignore")
					noPunct = ascii.translate(None, string.punctuation)
				elif type(lowers) is str:
					noPunct = lowers.translate(None, string.punctuation)
				noFaceDocuments.append(noPunct)
		except:
			pass

	lowers = sourceContent.lower()
	noFaceDocuments.insert(0, lowers)

	tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words="english")
	noFaceTfs = tfidf.fit_transform(noFaceDocuments)

	noFaceSimilarity = noFaceTfs * noFaceTfs.T

	similarities = []
	print("building similarities")
	print("face similarity length: %d" % noFaceSimilarity.get_shape()[1])
	for i in range(noFaceSimilarity.get_shape()[1]):
		similarities.append(noFaceSimilarity[0,i])

	indices = [i[0] for i in sorted(enumerate(similarities), key=lambda x:x[1], reverse=True)]

	for i in range(len(indices)):
		if len(noFaceSrcs) > indices[i]:
			sortedSrcs.append(noFaceSrcs[indices[i]])

	#end tfidf
	print "done doing tfidf"
	print "sortedSrcs: " + str(sortedSrcs)

	#return image sources sorted by url text cosine similarity to source content
	return sortedSrcs

# Test method, takes in a body of text and outputs the recognized entities in
# JSON.
@app.route('/er')
def extractEntities():
	text = request.args.get('text', '')
	ents = er.getEntities(text)
	return jsonify(ents)

# Boilerplate code to launch web server on startup
if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=True)
