# WARNING: this currently does not generate network links and may overwrite them

import io
import os
import math
import json
import pprint

DRAW_DIRECTORY = "../draw"
KML_DRAW_DIRECTORY = "../kml/draw"
MAIN_OUTPUT_KML_FILE = "../kml/improvement-drawings.kml"
DRAW_TYPE_LIST = ["d","D","l","L","w","W"]
LOWER_BOUND = 1
UPPER_BOUND = 100000
RESOLUTION = 10

# get drawing set list
drawingSetList = []
for (dirpath, dirnames, filenames) in os.walk( KML_DRAW_DIRECTORY ):
	drawingSetList.extend( filenames ) # filenames is a list

def rcsvlyBuildTree( lowerBound, upperBound, resolution ):

	branch = [ lowerBound, upperBound ] 

	size = math.floor( ( upperBound - ( lowerBound -1 ) ) / resolution ) # must be an integer
	#print( "size: " + str( size ) )

	if size >= resolution:
		branch.append( [] )
		for i in range( resolution ):
			thisLowerBound = i * size + lowerBound
			#print( "thisLowerBound: " + str( thisLowerBound ) )
			thisUpperBound = ( i + 1 ) * size + lowerBound - 1
			#print( " thisUpperBound: " + str( thisUpperBound ) )
			branch[ -1 ].append( rcsvlyBuildTree( thisLowerBound, thisUpperBound, resolution ) )
			if len( branch[ -1 ][ -1 ] ) == 2:
				#print( branch )
				del branch[ -1 ][ -1 ]
				#branch.pop()
				#print( branch )
		#print(branch)
		if len( branch[ -1 ] ) == 0:
			del branch[ -1 ]
		#print(branch)
	else:
		addDrawingSetList = []
		for i in range( resolution ):
			for drawingType in DRAW_TYPE_LIST:
				drawingSet = str( lowerBound + i ) + "-" + drawingType + ".kml"
				#print( "drawingSet: " + drawingSet )
				if drawingSet in drawingSetList:
					#print( "drawingSet: " + drawingSet )
					#print( "branch: " + str( branch ) )
					addDrawingSetList.append( drawingSet )
		if len( addDrawingSetList ) > 0:
			#print( "addDrawingSetList: " + str( addDrawingSetList ) )
			branch.append( addDrawingSetList )

		#print( "lowerBound: " + str( lowerBound ) )
		#print( "upperBound: " + str( upperBound ) )

	if len( branch ) == 3:
		if len( branch[ -1 ] ) == 0:
			branch = []

	return branch

tree = []
tree.append( rcsvlyBuildTree( LOWER_BOUND, UPPER_BOUND, RESOLUTION ) )

with io.open( "build-improvement-drawings-kml.log", "w", encoding="utf-8" ) as file:
	file.write( json.dumps( tree, indent=2 ) )

#print(strKml)

# Build improvement-drawings.kml
os.remove( MAIN_OUTPUT_KML_FILE )
with io.open( MAIN_OUTPUT_KML_FILE, "w", encoding="utf-8" ) as file:
	file.write( "<?xml"
	" version=\"1.0\""
	" encoding=\"UTF-8\"?>"
	"<kml"
	" xmlns=\"http://www.opengis.net/kml/2.2\""
	" xmlns:gx=\"http://www.google.com/kml/ext/2.2\""
	" xmlns:kml=\"http://www.opengis.net/kml/2.2\""
	" xmlns:atom=\"http://www.w3.org/2005/Atom\">"
	"<Folder>"
	"<name>Improvement Drawings</name>"
	"<visibility>0</visibility>"
	"<open>0</open>" )

	def rcsvlyWrite( branches ):
		for i in range( len( branches ) ):
			branch = branches[ i ]
			lowerBound = branch[ 0 ]
			upperBound = branch[ 1 ]
			folderName = str( lowerBound ) + " - " + str( upperBound )
			file.write( "\n<Folder>\n\t<name>" + folderName + "</name>\n\t<visibility>0</visibility>\n\t<open>0</open>" )
			if len( branch ) == 3:
				global RESOLUTION
				#print(upperBound - lowerBound)
				if upperBound - lowerBound > RESOLUTION:
					nextBranches = branch[2]
					#print("nextBranches:")
					#print(nextBranches)
					rcsvlyWrite( nextBranches )
				else:
					drawingList = branch[2]
					for drawing in drawingList:
						file.write(
							"<NetworkLink>"
							"<name>%s</name>"
							"<open>0</open>"
							"<visibility>1</visibility>"
							"<refreshVisibility>0</refreshVisibility>"
							"<Link>"
								"<href>draw/%s</href>"
								"<refreshMode>onInterval</refreshMode>"
								"<refreshInterval>60</refreshInterval>"
							"</Link>"
							"</NetworkLink>"
							% (drawing, drawing)
						)
						#print("drawing: " + drawing)
			file.write( "\n</Folder>")

	#print( tree[ 0 ] )
	branches = tree[ 0 ][ 2 ]
	#print("branches:")
	#print(branches)
	for i in range( len( branches ) ):
		branch = branches[ i ]
		lowerBound = branch[ 0 ]
		upperBound = branch[ 1 ]
		folderName = str( lowerBound ) + " - " + str( upperBound )
		file.write( "\n<Folder>\n\t<name>" + folderName + "</name>\n\t<visibility>0</visibility>\n\t<open>0</open>" )
		if len( branch ) == 3:
			if upperBound - lowerBound > RESOLUTION:
				nextBranches = branch[2]
				#print("nextBranches:")
				#print(nextBranches)
				rcsvlyWrite( nextBranches )
			else:
				drawingList = branch[2]
				#print("drawingList:") 
				#print(drawingList)
		file.write( "\n</Folder>")
	file.write( "\n</Folder>"
	"\n</kml>" )

# Rebuild drawing overlay kmls to specified drawing directory
for drawingSet in drawingSetList:
	readFilePath = KML_DRAW_DIRECTORY + "/" + drawingSet
	writeFilePath = readFilePath + ".tmp"
	if os.path.isfile( readFilePath ) == True:
		with io.open( readFilePath, "r", encoding="utf-8" ) as readFile:
			with io.open( writeFilePath, "w", encoding="utf-8" ) as writeFile:
				for line in readFile:
					if "<href>" in line:
						#print(line)
						arrLine = line.split("/")
						#print(arrLine)
						newArrLine = arrLine[ -3 : ] # get last 3 elements
						#print(newArrLine)
						newLine = "<href>../" + DRAW_DIRECTORY + "/" + "/".join( str( element ) for element in newArrLine ) # account for location of this script
						#print(newLine)
						writeFile.write( newLine )
					else:
						writeFile.write( line )
		os.remove( readFilePath )
		os.rename( writeFilePath, readFilePath )
