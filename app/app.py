from flask import jsonify, Flask, render_template, request, Markup
import cssutils, unicodedata
from bs4 import BeautifulSoup
app = Flask(__name__)

@app.route('/')
def form():
   return render_template('form.html')

@app.route('/doc')
def doc():
   return render_template('doc.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.get_data()
      converted = convert(result)
      return jsonify(**converted)


def convert(form):
    converted = toBootstrap(form)
    return {'original': form, 'converted': Markup(converted)}

def toBootstrap(form):
    soup = BeautifulSoup(form)
    while True:  # Change tbody tags to div.containers . This works for bootstrap because .containers are stackable(but not container-fluid)
        tbody = soup.find('tbody')
        if not tbody:
            break
        tbody.name = 'div'
        tbody['class'] = tbody.get('class', []) + ['containers']

    while True:  # Change table tags to div.containers
        table = soup.find('table')
        if not table:
            break
        table.name = 'div'
        table['class'] = table.get('class', []) + ['containers']

    while True:  # Change tr to div.row
        tr = soup.find('tr')
        if not tr:
            break
        tr.name = 'div'
        tr['class'] = tr.get('class', []) + ['row']

    while True: # Change td to columns. The xs is for smaller screens. sm is for bigger. These can be changed easily later for fit the layout needs.
        td = soup.find('td')
        if not td:
            break
        td.name = 'div'
        td['class'] = td.get('class', []) + ['col-xs-12', 'col-sm-12']

    divs = soup.findAll('div') # Strip every width, height and text-align inline css style.
    for div in divs:
        css = cssutils.parseStyle(div.get('style', ''))
        del css['width']
        del css['height']
        del css['text-align']
        del css['vertical-align']
        div['style'] = css.cssText

    while True: # Recusively delete the empty p div span tags. On the websites they are often used to add space. This is not a common practice and won't work for most browsers.
       # empty = soup.find(lambda tag: tag.name in ['p','div','span'] and (not tag.contents and (tag.string == None or len(tag.string)<=6)))
       empty = soup.find(lambda tag: tag.name in ['p','div','span'] and tag.find(True) is None and (tag.string is None or tag.string.strip()==""))
       if not empty:
           break
       print empty
       empty.extract()
    for tag in soup():
        del tag['align']
        del tag['valign']
        del tag['width']
        del tag['height']
        del tag['max-width']
        del tag['max-height']
    return soup

