from HTMLParser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc

#http://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
class _DeHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = []

    def handle_data(self, data):
        text = data.strip()
        if len(text) > 0:
            text = sub('[ \t\r\n]+', ' ', text)
            self.__text.append(text + ' ')

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.__text.append('\n\n')
        elif tag == 'br':
            self.__text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__text.append('\n\n')

    def text(self):
        return ''.join(self.__text).strip()


def dehtml(text):
    try:
        parser = _DeHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.text()
    except:
        print_exc(file=stderr)
        return text


def main():
    text = r'''
        <html>
            <body>
                <p>Project:</p> DeHTML<br>
                <p>Description</p>:<br>
                This small script is intended to allow conversion from HTML markup to 
                plain text.
                <div class="col col-50 col-9 here-is-what thisisa" id="chart_div">
                    <button on-click="hereWeGo()">Button text to parse.</button>
                    <form>
                        <input type="text"></input>
                    </form>
                </div>
                <div><h1>Big header to parse.</h1></div>
                <p>Paragraph to parse.</p>
            </body>
        </html>
    '''
    print(dehtml(text))


if __name__ == '__main__':
    main()