# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.item import Field


class VesselfinderItem(scrapy.Item):
    Recent_ports = Field()
    Ais_type = Field()
    Ship_type = Field()
    Flag = Field()
    Destination = Field()
    ETA = Field()
    Position_received = Field()
    Name = Field()
    Gross_tonnage = Field()
    Summer_deadweight = Field()
    Year_of_built = Field()
    Owner_and_year = Field()
    links = Field()
    Coordinates = Field()


