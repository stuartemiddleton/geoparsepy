import os, sys, logging, traceback, codecs, datetime, copy, time, ast, math, re, random, shutil, json
import soton_corenlppy, geoparsepy

LOG_FORMAT = ('%(message)s')
logger = logging.getLogger( __name__ )
logging.basicConfig( level=logging.INFO, format=LOG_FORMAT )
logger.info('logging started')

dictFocusAreaSpec = {
	'southampton' : {
		'focus_area_id' : 'southampton',
		'admin': ['southampton','south east england', 'united kingdom'],
		'admin_lookup_table' : 'global_cities_admin',
	}
}

dictGlobalSpec = None

dictGeospatialConfig = geoparsepy.geo_parse_lib.get_geoparse_config( 
	lang_codes = ['en'],
	logger = logger,
	whitespace = u'"\u201a\u201b\u201c\u201d()',
	sent_token_seps = ['\n','\r\n', '\f', u'\u2026'],
	punctuation = """,;\/:+-#~&*=!?""",
	)

dbHandlerPool = {}
dbHandlerPool['admin'] = soton_corenlppy.PostgresqlHandler.PostgresqlHandler( 'postgres', 'postgres', 'localhost', 5432, 'openstreetmap' )
dbHandlerPool['point'] = soton_corenlppy.PostgresqlHandler.PostgresqlHandler( 'postgres', 'postgres', 'localhost', 5432, 'openstreetmap' )
dbHandlerPool['poly'] = soton_corenlppy.PostgresqlHandler.PostgresqlHandler( 'postgres', 'postgres', 'localhost', 5432, 'openstreetmap' )
dbHandlerPool['line'] = soton_corenlppy.PostgresqlHandler.PostgresqlHandler( 'postgres', 'postgres', 'localhost', 5432, 'openstreetmap' )

for strFocusArea in dictFocusAreaSpec.keys() :
	logger.info( 'starting focus area ' + strFocusArea )
	jsonFocusArea = dictFocusAreaSpec[strFocusArea]
	geoparsepy.geo_preprocess_lib.create_preprocessing_tables( jsonFocusArea, dbHandlerPool['admin'], 'public', delete_contents = False, logger = logger )
	dictNewLocations = geoparsepy.geo_preprocess_lib.execute_preprocessing_focus_area( jsonFocusArea, dbHandlerPool, 'public', logger = logger )
	logger.info( 'finished focus area ' + strFocusArea )
	logger.info( 'location id range : ' + repr(dictNewLocations) )

dbHandlerPool['admin'].close()
dbHandlerPool['point'].close()
dbHandlerPool['poly'].close()
dbHandlerPool['line'].close()
