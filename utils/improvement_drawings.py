# WARNING: this currently does not generate network links and may overwrite them

import io
import os

lowerBound = 1
drawNumMax = 100000
drawNumDiv = 10

strKml = (
	"<?xml"
	" version=\"1.0\""
	" encoding=\"UTF-8\"?>\n"
	"<kml"
	" xmlns=\"http://www.opengis.net/kml/2.2\""
	" xmlns:gx=\"http://www.google.com/kml/ext/2.2\""
	" xmlns:kml=\"http://www.opengis.net/kml/2.2\""
	" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n"
	"<Folder>\n"
	"\t<name>Improvement Drawings</name>\n"
	"\t<visibility>0</visibility>\n"
	"\t<open>0</open>\n"
)

def recursiveFunction( tabCount, lowerBound, drawNumMax, drawNumDiv ):
	if drawNumMax < drawNumDiv: # Abort function if already at lowest division possible
		return
	global strKml
	tabCount += 1
	strTabs = ""
	for i in range( 1, tabCount ):
			strTabs += "\t"
	startAt = lowerBound - 1
	for i in range( 0, drawNumDiv ):
		strKml += strTabs + "<Folder>\n"
		newMax = round( drawNumMax / drawNumDiv )
		#print( "a", startAt )
		lowerBound = round( newMax * i + 1 + startAt )
		#print( "b", lowerBound )
		upperBound = round( newMax * ( i + 1 ) + startAt )
		strKml += (
			strTabs + "\t<name>" + str( lowerBound ) + " – " + str( upperBound ) + "</name>\n"
			+ strTabs + "\t<visibility>0</visibility>\n"
			+ strTabs + "\t<open>0</open>\n"
		)
		#print( "<name>" + str( lowerBound ) + " – " + str( upperBound ) + "</name>" )
		#print( "c", newMax )
		if newMax > drawNumDiv:
			#print( "d", lowerBound )
			#print( "e", startAt )
			recursiveFunction( tabCount, lowerBound, newMax, drawNumDiv )
		strKml += strTabs + "</Folder>\n"
	return

recursiveFunction( 1, lowerBound, drawNumMax, drawNumDiv )

strKml += (
	"</Folder>\n"
	"</kml>"
)

#print(strKml)

with io.open( "improvement_drawings.kml", "w", encoding="utf-8" ) as file:
	file.write( strKml )