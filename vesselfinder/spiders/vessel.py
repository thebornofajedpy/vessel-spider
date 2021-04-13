# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import VesselfinderItem
from itertools import zip_longest

class VesselSpider(scrapy.Spider):
    name = 'vessel'
    allowed_domains = ['www.vesselfinder.com']
    #start_urls = ['https://www.vesselfinder.com/vessels']

    def __init__(self):
        self.items = VesselfinderItem()
        self.types = {"Any type": "-1", "General / Dry cargo":"4", "Bulk carrier": "402", "Container / Reefer": "401",
                      "Tanker":"6","LNG / LPG / CO2 Tanker":"601","Chemical Tanker":"602", "Oil Tanker":"603",
                      "Passenger / Cruise":"3","High speed craft":"2","Yacht / Pleasure craft":"8","Fishing":"5",
                      "Offshore":"901","Military":"7","Auxiliary":"0","Other / Unknown type":"1"}
        print("----------------------------------------------")
        print(self.types)
        print("Choose type :")
        self.input = str(input())
        print("----------------------------------------------")

    def start_requests(self):
        yield scrapy.Request('https://www.vesselfinder.com/vessels?type={0}'.format(self.input),callback=self.parse)

    def parse(self,response):
        pages = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "vfix", " " ))]//span/text()').re(r'/ (.*)')[0]
        pages = pages.replace(',','')
        print("The number of pages are : {0} ".format(pages))
        print("----------------------------------------------")

        for i in range(1, int(pages)):
            yield scrapy.Request('https://www.vesselfinder.com/vessels?page={0}&type={1}'.format(i,self.input),callback=self.parse2)

    def parse2(self, response):
        links = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ship-link", " " ))]/@href').extract()
        names = response.xpath('//a[@class="ship-link"]/text()').re(r'[A-Za-z0-9].*[A-Za-z0-9]')
        for i, j in zip(links, names):
            yield scrapy.Request('https://www.vesselfinder.com{0}'.format(i), callback=self.parse3, meta={"links": i, "names": j})

    def parse3(self, response):
        MMSI = response.css('.npr tr:nth-child(5) .v3::text').re(r'/ (.*)')
        IMO = response.css('.npr tr:nth-child(5) .v3::text').re(r'(.*) /')
        link = response.meta['links']
        Ais_type = response.css('.npr tr:nth-child(1) .v3::text').extract()
        Ship_type = response.css('.ad-c0+ .ship-section tr:nth-child(3) .v3::text').extract()
        Flag = response.css('.npr tr:nth-child(2) .v3::text').extract()
        Destination = response.css('.npr tr:nth-child(3) .v3::text').extract()
        ETA = response.css('.npr tr:nth-child(4) .v3::text').extract()
        Position_received = response.xpath('//*[@id="lastrep"]/@data-title').extract()
        Name = response.meta['names']
        Gross_tonnage = response.css('.ad-c0+ .ship-section tr:nth-child(6) .v3::text').extract()
        Summer_deadweight = response.css('.ad-c0+ .ship-section tr:nth-child(7) .v3::text').extract()
        Year_of_built = response.css('.ad-c0+ .ship-section tr:nth-child(11) .v3::text').extract()
        Owner = response.css('.v4::text').extract()
        year = response.css('.v5::text').extract()
        Owner_and_year = list(zip_longest(Owner,year))
        #Owner_and_year = response.css('.v5::text , .v4::text').extract()
        Coordinates = response.css('.npr tr:nth-child(10) .v3::text').extract()
        yield scrapy.Request(url='https://www.vesselfinder.com/api/pro/portcalls/{0}?s"'.format(MMSI[0]),
                             callback=self.parse4,headers = {
                            'Connection': 'keep-alive',
                            'Pragma': 'no-cache',
                            'Cache-Control': 'no-cache',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
                            'Sec-Fetch-Dest': 'empty',
                            'Accept': '*/*',
                            'Sec-Fetch-Site': 'same-origin',
                            'Sec-Fetch-Mode': 'cors',
                            'Accept-Language': 'en-US,en;q=0.9',
                        },cookies= {
                            '_ga': 'GA1.2.2114378854.1581071711',
                            '_gid': 'GA1.2.512151660.1581071711',
                            'vfatid': '{0}'.format(response.xpath('//meta[@name="at"]/@content').extract()[0]),
                            '_gat': '1',
                        },meta={'MMSI': MMSI, 'IMO': IMO, 'Ais_type': Ais_type, 'Ship_type': Ship_type, 'Flag': Flag,
                                'Destination': Destination, 'ETA': ETA, 'Position_received': Position_received,
                                'Name': Name, 'Gross_tonnage': Gross_tonnage, 'Summer_deadweight': Summer_deadweight,
                                'Year_of_built': Year_of_built, 'Owner_and_year': Owner_and_year, 'Coordinates': Coordinates}
                             )

    def parse4(self,response):
        js = json.loads(response.body_as_unicode())
        try:
            ports = []
            for i in js:
                ports.append(i['PORTCALL'])
        except:
            ports = []
        self.items['Recent_ports'] = ports
        self.items['Ais_type'] = response.meta['Ais_type']
        self.items['Ship_type'] = response.meta['Ship_type']
        self.items['Flag'] = response.meta['Flag']
        self.items['Destination'] = response.meta['Destination']
        self.items['ETA'] = response.meta['ETA']
        self.items['Position_received'] = response.meta['Position_received']
        self.items['Name'] = response.meta['Name']
        self.items['Gross_tonnage'] = response.meta['Gross_tonnage']
        self.items['Summer_deadweight'] = response.meta['Summer_deadweight']
        self.items['Year_of_built'] = response.meta['Year_of_built']
        self.items['Owner_and_year'] = response.meta['Owner_and_year']
        self.items['Coordinates'] = response.meta['Coordinates']
        yield self.items

