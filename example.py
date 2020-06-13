import os, sys, logging, traceback, codecs, datetime, copy, time, ast, math, re, random, shutil, json
import soton_corenlppy, geoparsepy

LOG_FORMAT = ('%(message)s')
logger = logging.getLogger( __name__ )
logging.basicConfig( level=logging.INFO, format=LOG_FORMAT )
logger.info('logging started')

dictGeospatialConfig = geoparsepy.geo_parse_lib.get_geoparse_config( 
	lang_codes = ['en'],
	logger = logger,
	whitespace = u'"\u201a\u201b\u201c\u201d()',
	sent_token_seps = ['\n','\r\n', '\f', u'\u2026'],
	punctuation = """,;\/:+-#~&*=!?""",
	)

databaseHandle = soton_corenlppy.PostgresqlHandler.PostgresqlHandler( 'postgres', 'postgres', 'localhost', 5432, 'openstreetmap', 600 )

dictLocationIDs = {}
listFocusArea=[ 'global_cities', 'europe_places', 'north_america_places', 'uk_places' ]
for strFocusArea in listFocusArea :
	dictLocationIDs[strFocusArea + '_admin'] = [-1,-1]
	dictLocationIDs[strFocusArea + '_poly'] = [-1,-1]
	dictLocationIDs[strFocusArea + '_line'] = [-1,-1]
	dictLocationIDs[strFocusArea + '_point'] = [-1,-1]

cached_locations = geoparsepy.geo_preprocess_lib.cache_preprocessed_locations( databaseHandle, dictLocationIDs, 'public', dictGeospatialConfig )
logger.info( 'number of cached locations = ' + str(len(cached_locations)) )

databaseHandle.close()

indexed_locations = geoparsepy.geo_parse_lib.calc_inverted_index( cached_locations, dictGeospatialConfig )
logger.info( 'number of indexed phrases = ' + str(len(indexed_locations.keys())) )

indexed_geoms = geoparsepy.geo_parse_lib.calc_geom_index( cached_locations )
logger.info( 'number of indexed geoms = ' + str(len(indexed_geoms.keys())) )

osmid_lookup = geoparsepy.geo_parse_lib.calc_osmid_lookup( cached_locations )

dictGeomResultsCache = {}

listText = [
	u'hello New York, USA its Bill from Bassett calling',
	u'live on the BBC Victoria Derbyshire is visiting Derbyshire for an exclusive UK interview',
	]

listTokenSets = []
listGeotags = []
for nIndex in range(len(listText)) :
	strUTF8Text = listText[ nIndex ]
	listToken = soton_corenlppy.common_parse_lib.unigram_tokenize_text( text = strUTF8Text, dict_common_config = dictGeospatialConfig )
	listTokenSets.append( listToken )
	listGeotags.append( None )

listMatchSet = geoparsepy.geo_parse_lib.geoparse_token_set( listTokenSets, indexed_locations, dictGeospatialConfig )

strGeom = 'POINT(-1.4052268 50.9369033)'
listGeotags[0] = strGeom

listMatchGeotag = geoparsepy.geo_parse_lib.reverse_geocode_geom( [strGeom], indexed_geoms, dictGeospatialConfig )
if len( listMatchGeotag[0] ) > 0  :
	for tupleOSMIDs in listMatchGeotag[0] :
		setIndexLoc = osmid_lookup[ tupleOSMIDs ]
		for nIndexLoc in setIndexLoc :
			strName = cached_locations[nIndexLoc][1]
			logger.info( 'Reverse geocoded geotag location [index ' + str(nIndexLoc) + ' osmid ' + repr(tupleOSMIDs) + '] = ' + strName )

for nIndex in range(len(listMatchSet)) :
	logger.info( 'Text = ' + listText[nIndex] )
	listMatch = listMatchSet[ nIndex ]
	strGeom = listGeotags[ nIndex ]
	setOSMID = set([])
	for tupleMatch in listMatch :
		nTokenStart = tupleMatch[0]
		nTokenEnd = tupleMatch[1]
		tuplePhrase = tupleMatch[3]
		for tupleOSMIDs in tupleMatch[2] :
			setIndexLoc = osmid_lookup[ tupleOSMIDs ]
			for nIndexLoc in setIndexLoc :
				logger.info( 'Location [index ' + str(nIndexLoc) + ' osmid ' + repr(tupleOSMIDs) + ' @ ' + str(nTokenStart) + ' : ' + str(nTokenEnd) + '] = ' + ' '.join(tuplePhrase) )
				break
	listLocMatches = geoparsepy.geo_parse_lib.create_matched_location_list( listMatch, cached_locations, osmid_lookup )
	geoparsepy.geo_parse_lib.filter_matches_by_confidence( listLocMatches, dictGeospatialConfig, geom_context = strGeom, geom_cache = dictGeomResultsCache )
	geoparsepy.geo_parse_lib.filter_matches_by_geom_area( listLocMatches, dictGeospatialConfig )
	geoparsepy.geo_parse_lib.filter_matches_by_region_of_interest( listLocMatches, [-148838, -62149], dictGeospatialConfig )
	setOSMID = set([])
	for nMatchIndex in range(len(listLocMatches)) :
		nTokenStart = listLocMatches[nMatchIndex][1]
		nTokenEnd = listLocMatches[nMatchIndex][2]
		tuplePhrase = listLocMatches[nMatchIndex][3]
		strGeom = listLocMatches[nMatchIndex][4]
		tupleOSMID = listLocMatches[nMatchIndex][5]
		dictOSMTags = listLocMatches[nMatchIndex][6]
		if not tupleOSMID in setOSMID :
			setOSMID.add( tupleOSMID )
			listNameMultilingual = geoparsepy.geo_parse_lib.calc_multilingual_osm_name_set( dictOSMTags, dictGeospatialConfig )
			strNameList = ';'.join( listNameMultilingual )
			strOSMURI = geoparsepy.geo_parse_lib.calc_OSM_uri( tupleOSMID, strGeom )
			logger.info( 'Disambiguated Location [index ' + str(nMatchIndex) + ' osmid ' + repr(tupleOSMID) + ' @ ' + str(nTokenStart) + ' : ' + str(nTokenEnd) + '] = ' + strNameList + ' : ' + strOSMURI )
