#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from datasheet import CSVFile
from surfer import Surfer
import csv
import cStringIO
import codecs


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

print "setting up browser..."
surfer = Surfer(browser="firefox")

result = []

postcode_groups = CSVFile("postnummergrupper_test.csv")
for postcode in postcode_groups.get_next():
    pnr = str(postcode["pnr"])
    print "scraping prefix %s" % pnr

    print "loading page..."
    surfer.surf_to("http://services3.posten.se/soktjanst/odr/odr.jspv")

    print "submitting form..."
    input_element_list = surfer.get_element_list('//input[@id="villkor3"]')
    input_element_list[0].send_keys(pnr)
    surfer.click_on_stuff("//button[@title='Sök']")

    print "fetching result..."
    result_elements = surfer.get_element_list("//tr[not(@id='')]")

    print "number of rows",
    print len(result_elements)

    for result_element in result_elements:
        cells = result_element.find_elements_by_xpath("td")
        # Is this a content row
        if len(cells) == 7:
            result_row = []
            for cell in cells:
                html = cell.get_attribute('innerHTML').replace("&nbsp;", "")
                result_row.append(html)
            print result_row
            result.append(result_row)

with open('output.csv', 'wb') as f:
    writer = UnicodeWriter(f)
    for row in result:
        writer.writerow(row)
