# geoparsepy project

geoparsepy is a Python geoparsing library that will extract and disambiguate locations from text. It uses a local OpenStreetMap database which allows very high and unlimited geoparsing throughput, unlike approaches that use a third-party geocoding service (e.g.  Google Geocoding API).

Geoparsing is based on named entity matching against OpenStreetMap (OSM) locations. All locations with names that match tokens will be selected from a target text sentence. This will result in a set of OSM locations, all with a common name or name variant, for each token in the text. Geoparsing included the following features:
  * **token expansion** using location name variants (i.e. OSM multi-lingual names, short names and acronyms)
  * **token expansion** using location type variants (e.g. street, st.)
  * **token filtering** of single token location names against WordNet (non-nouns), language specific stoplists and peoples first names (nltk.corpus.names.words()) to reduce false positive matches
  * **prefix checking** when matching in case a first name prefixes a location token(s) to avoid matching peoples full names as locations (e.g. Victoria Derbyshire != Derbyshire)

Location disambiguation is the process of choosing which of a set of possible OSM locations, all with the same name, is the best match. Location disambiguation is based on an evidential approach, with evidential features detailed below in order of importance:
  * **token subsumption**, rejecting smaller phrases over larger ones (e.g. 'New York' will prefer [New York, USA] to [York, UK])
  * **nearby parent region**, preferring locations with a parent region also appearing within a semantic distance (e.g. 'New York in USA' will prefer [New York, USA] to [New York, BO, Sierra Leone])
  * **nearby locations**, preferring locations with closeby or overlapping locations within a semantic distance (e.g. 'London St and Commercial Road' will select from road name choices with the same name based on spatial proximity)
  * **nearby geotag**, preferring locations that are closeby or overlapping a geotag
  * **general before specific**, rejecting locations with a higher admin level (or no admin level at all) compared to locations with a lower admin level (e.g. 'New York' will prefer [New York, USA] to [New York, BO, Sierra Leone]

Currently the following languages are supported:
  * English, French, German, Italian, Portuguese, Russian, Ukrainian
  * All other languages will work but there will be no language specific token expansion available

geoparsepy works with Python 3.7 and has been tested on Windows 10 and Ubuntu 18.04 LTS.

This geoparsing algorithm uses a large memory footprint (e.g. 12 Gbytes RAM for global cities), RAM size proportional to the number of cached locations, to maximize matching speed. It can be naively parallelized, with multiple geoparse processes loaded with different sets of locations and the geoparse results aggregated in a last process where location disambiguation is applied. This approach has been validated across an APACHE Storm cluster.

The software is copyright 2020 [University of Southampton](https://www.ecs.soton.ac.uk/people/sem03), UK. It was created over a multi-year period under EU FP7 projects TRIDEC (258723), REVEAL (610928), InnovateUK project LPLP (104875) and ESRC project FloraGuard (ES/R003254/1). This software can only be used for research, education or evaluation purposes. A free commercial license is available on request to {sem03}@soton.ac.uk. The University of Southampton is open to discussions regarding [collaboration](https://www.southampton.ac.uk/~sem03/engagement.html) in future research projects relating to this work.

Feature suggestions and/or bug reports can be sent to {sem03}@soton.ac.uk. We do not however offer any software support beyond the examples and API documentation already provided.


# Scientific publications
Middleton, S.E. Middleton, L. Modafferi, S. [Real-time Crisis Mapping of Natural Disasters using Social Media](http://eprints.soton.ac.uk/370581/), Intelligent Systems, IEEE , vol.29, no.2, pp.9,17, Mar.-Apr. 2014

Middleton, S.E. Krivcovs, V. [Geoparsing and Geosemantics for Social Media: Spatio-Temporal Grounding of Content Propagating Rumours to support Trust and Veracity Analysis during Breaking News](http://eprints.soton.ac.uk/390820/), ACM Transactions on Information Systems (TOIS), 34, 3, Article 16 (April 2016), 26 pages. DOI=10.1145/2842604

Middleton, S.E. Kordopatis-Zilos, G. Papadopoulos, S. Kompatsiaris, Y. [Location Extraction from Social Media: Geoparsing, Location Disambiguation, and Geotagging](https://www.southampton.ac.uk/~sem03/middleton_tois_2018.pdf), ACM Transactions on Information Systems (TOIS) 36, 4, Article 40 (June 2018), 27 pages. DOI: https://doi.org/10.1145/3202662. Presented at SIGIR 2019

A benchmark geoparse dataset is also available for free from the University of Southampton on request via email to {sem03}@soton.ac.uk.


# geoparsepy documentation resources

geoparsepy [API](https://www.southampton.ac.uk/~sem03/geoparsepy/api/index.html)
geoparsepy example code on [github](https://github.com/stuartemiddleton/geoparsepy)

# Python libs needed (earlier versions may be suitable but are untested)

Python libs: psycopg2 >= 2.8, nltk >= 3.4, numpy >= 1.18, shapely >= 1.6, setuptools >= 46
Database: PostgreSQL >= 11.3, PostGIS >= 2.5

For LINUX deployments the following is needed:

```
sudo apt-get install libgeos-dev libgeos-3.4.2 libpq-dev
```

You will need to download NLTK corpra before running geoparsepy:

```python
python
import nltk
nltk.download()
==> install all or at least stopwords, names and wordnet
```

# Installation

python3 -m pip install geoparsepy

# Databases needed for geoparsing
Download pre-processed SQL table dumps from OSM image dated dec 2019

```
[geoparsepy_preprocessed_tables.tar.gz](https://www.southampton.ac.uk/~sem03/geoparsepy/geoparsepy_preprocessed_tables.tar.gz) 1.4 GB
```

Connect to PostgreSQL and create the database with the required PostGIS and hstore extensions

```
psql -U postgres
CREATE DATABASE openstreetmap;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
CREATE EXTENSION IF NOT EXISTS hstore;
```

Import the precomputed database tables for global cities and places

```
psql -d openstreetmap -f global_cities.sql
psql -d openstreetmap -f uk_places.sql
psql -d openstreetmap -f north_america_places.sql
psql -d openstreetmap -f europe_places.sql
```

# Example code geoparse (start here)

Geoparse some text using the default focus areas in the Postgres database. Fully documented example PY file can be found at geoparsepy.example_geoparse.py
note: loading 300,000+ global locations into memory at startup is slow (10 minutes) but subsequently the geoparsing of text is very fast (real-time speeds)

```python
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
```


# Example geoparse output
```
logging started
loading stoplist from C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-geo-stoplist-en.txt
loading whitelist from C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-geo-whitelist.txt
loading blacklist from C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-geo-blacklist.txt
loading building types from C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-buildingtype-en.txt
loading location type corpus C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-buildingtype-en.txt
- 3 unique titles
- 76 unique types
loading street types from C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-streettype-en.txt
loading location type corpus C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-streettype-en.txt
- 15 unique titles
- 32 unique types
loading admin types from C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-admintype-en.txt
loading location type corpus C:\Program Files\Python3\lib\site-packages\geoparsepy\corpus-admintype-en.txt
- 14 unique titles
- 0 unique types
loading gazeteer from C:\Program Files\Python3\lib\site-packages\geoparsepy\gazeteer-en.txt
caching locations : {'global_cities_admin': [-1, -1], 'global_cities_poly': [-1, -1], 'global_cities_line': [-1, -1], 'global_cities_point': [-1, -1], 'europe_places_admin': [-1, -1], 'europe_places_poly': [-1, -1], 'europe_places_line': [-1, -1], 'europe_places_point': [-1, -1], 'north_america_places_admin': [-1, -1], 'north_america_places_poly': [-1, -1], 'north_america_places_line': [-1, -1], 'north_america_places_point': [-1, -1], 'uk_places_admin': [-1, -1], 'uk_places_poly': [-1, -1], 'uk_places_line': [-1, -1], 'uk_places_point': [-1, -1]}
number of cached locations = 800820
number of indexed phrases = 645697
number of indexed geoms = 657264
Reverse geocoded geotag location [index 190787 osmid (253067120,)] = Bassett
Reverse geocoded geotag location [index 779038 osmid (253067120,)] = Bassett
Text = hello New York, USA its Bill from Bassett calling
Location [index 792265 osmid (29457403,) @ 1 : 2] = new york
Location [index 737029 osmid (151937435,) @ 1 : 2] = new york
Location [index 737030 osmid (316976734,) @ 1 : 2] = new york
Location [index 140096 osmid (-175905,) @ 1 : 2] = new york
Location [index 737028 osmid (61785451,) @ 1 : 2] = new york
Location [index 792266 osmid (2218262347,) @ 1 : 2] = new york
Location [index 146732 osmid (-61320,) @ 1 : 2] = new york
Location [index 126105 osmid (-134353,) @ 2 : 2] = york
Location [index 758451 osmid (153595296,) @ 2 : 2] = york
Location [index 758454 osmid (153968758,) @ 2 : 2] = york
Location [index 114051 osmid (-1425436,) @ 2 : 2] = york
Location [index 758455 osmid (158656063,) @ 2 : 2] = york
Location [index 758452 osmid (153924230,) @ 2 : 2] = york
Location [index 758450 osmid (153473841,) @ 2 : 2] = york
Location [index 758449 osmid (151672942,) @ 2 : 2] = york
Location [index 758458 osmid (316990182,) @ 2 : 2] = york
Location [index 758448 osmid (151651405,) @ 2 : 2] = york
Location [index 800785 osmid (20913294,) @ 2 : 2] = york
Location [index 758447 osmid (151528825,) @ 2 : 2] = york
Location [index 140948 osmid (-148838,) @ 4 : 4] = usa
Location [index 190787 osmid (253067120,) @ 8 : 8] = bassett
Location [index 705552 osmid (151840681,) @ 8 : 8] = bassett
Location [index 705551 osmid (151463868,) @ 8 : 8] = bassett
Disambiguated Location [index 0 osmid (-61320,) @ 1 : 2] = New York;NY;New York State : http://www.openstreetmap.org/relation/61320
Disambiguated Location [index 3 osmid (-148838,) @ 4 : 4] = United States;US;USA;United States of America : http://www.openstreetmap.org/relation/148838
Disambiguated Location [index 5 osmid (253067120,) @ 8 : 8] =  : http://www.openstreetmap.org/node/253067120
Text = live on the BBC Victoria Derbyshire is visiting Derbyshire for an exclusive UK interview
Location [index 87080 osmid (-2316741,) @ 4 : 4] = victoria
Location [index 177879 osmid (-10307525,) @ 4 : 4] = victoria
Location [index 754399 osmid (154301948,) @ 4 : 4] = victoria
Location [index 45074 osmid (-5606595,) @ 4 : 4] = victoria
Location [index 595897 osmid (385402175,) @ 4 : 4] = victoria
Location [index 595901 osmid (462241727,) @ 4 : 4] = victoria
Location [index 754403 osmid (158651084,) @ 4 : 4] = victoria
Location [index 754358 osmid (151336948,) @ 4 : 4] = victoria
Location [index 128827 osmid (-407423,) @ 4 : 4] = victoria
Location [index 595902 osmid (463188523,) @ 4 : 4] = victoria
Location [index 595899 osmid (447925715,) @ 4 : 4] = victoria
Location [index 595898 osmid (435240340,) @ 4 : 4] = victoria
Location [index 597713 osmid (277608416,) @ 4 : 4] = victoria
Location [index 45017 osmid (-5606596,) @ 4 : 4] = victoria
Location [index 775444 osmid (30189922,) @ 4 : 4] = victoria
Location [index 87296 osmid (-2256643,) @ 4 : 4] = victoria
Location [index 754364 osmid (151395812,) @ 4 : 4] = victoria
Location [index 157847 osmid (74701108,) @ 4 : 4] = victoria
Location [index 754393 osmid (151521359,) @ 4 : 4] = victoria
Location [index 161280 osmid (75538688,) @ 4 : 4] = victoria
Location [index 595900 osmid (460070685,) @ 4 : 4] = victoria
Location [index 754369 osmid (151476805,) @ 4 : 4] = victoria
Location [index 99056 osmid (-1828436,) @ 4 : 4] = victoria
Location [index 126056 osmid (-195384,) @ 8 : 8] = derbyshire
Location [index 146796 osmid (-62149,) @ 12 : 12] = uk
Disambiguated Location [index 0 osmid (-195384,) @ 8 : 8] = Derbyshire : http://www.openstreetmap.org/relation/195384
Disambiguated Location [index 2 osmid (-62149,) @ 12 : 12] = United Kingdom;GB;GBR;UK : http://www.openstreetmap.org/relation/62149
```

# Databases needed for preprocessing focus areas (optional)
To preprocess your own focus areas (e.g. a city with all its streets and buildings) you need a local deployment of the planet OpenStreetmapDatabase. Once a focus area is preprocessed a database table will be created for it. This can be used in the geoparse just like the 'global_cities' focus area is in the previous example. Instructions below are dated dec 2020, refer to links for more up-to-date information.

[Osm2pgsql](http://wiki.openstreetmap.org/wiki/Osm2pgsql#From_the_package_manager)
[Planet.osm](http://wiki.openstreetmap.org/wiki/Planet.osm)

```
# Download OpenStreetMap map data archive
- http://wiki.openstreetmap.org/wiki/Planet.osm
  + pick a mirror and download planet-latest.osm.bz2 file
  + all maps are WGS84 coord system
  + this will give you a .bz2 compressed .pbf file with the OSM dataset for the country specified
- see https://github.com/openstreetmap/osm2pgsql

# remove postgres (old versions - might not be needed if clean install)
sudo apt list --installed | grep post
sudo apt-get remove --purge postgresql-10
sudo apt-get remove --purge postgresql-10-postgis-2.4-scripts
sudo apt-get remove --purge postgis

# install using a version number (otherwise get problems later)
sudo apt-get install python3-apt
sudo apt-get install postgresql-10-postgis-2.4

# print versions
pg_config --version
psql --version

sudo /etc/init.d/postgresql stop
sudo /etc/init.d/postgresql status

sudo nano /etc/postgresql/10/main/pg_hba.conf
host    all             all             127.0.0.1/32            md5
host    all             all             127.0.0.1/32            trust

sudo nano /etc/postgresql/10/main/postgresql.conf
+ listen_addresses = '*'
+ shared_buffers = 512MB
+ work_mem = 512MB
+ maintenance_work_mem = 2GB
+ max_worker_processes = 16
+ max_parallel_workers_per_gather = 8
+ max_parallel_workers = 16
+ constraint_exclusion = partition

sudo /etc/init.d/postgresql start
sudo /etc/init.d/postgresql status

# check postgresql is running OK
sudo netstat -nlp | grep 5432
sudo cat /var/log/postgresql/postgresql-10-main.log

# make postgis database (empty initially)
sudo -u postgres createdb openstreetmap
sudo -u postgres psql -d openstreetmap -c 'CREATE EXTENSION postgis; CREATE EXTENSION hstore;'
sudo -u postgres psql -d openstreetmap -c "SELECT * FROM information_schema.tables WHERE table_schema = 'public'"

# install osm
sudo mkdir /var/lib/osm
cd /var/lib/osm
sudo wget http://ftp.snt.utwente.nl/pub/misc/openstreetmap/planet-latest.osm.bz2

# make flat node file (as planet OSM is too large otherwise for RAM)
sudo mkdir /var/lib/osm/flat-nodes
sudo chown -R postgres /var/lib/osm/flat-nodes

# run osm2pgsql (will take about 7 days to finish so redirect stderr and stdout to file and run as a deamon process)
sudo apt-get install osm2pgsql
sudo -u postgres osm2pgsql -c -d openstreetmap -P 5432 -E 4326 -S /usr/share/osm2pgsql/default.style -k -s -C 8192 --flat-nodes /var/lib/osm/flat-nodes/flat-node-index-file --number-processes 8 /var/lib/osm/planet-latest.osm.bz2 > /var/lib/osm/osm2pgsql-stdout.log 2>&1 &
sudo -u postgres psql -d openstreetmap -c "SELECT * FROM information_schema.tables WHERE table_schema = 'public'"
```

# Example code preprocess focus area (optional)

Preprocessing new focus area tables in the Postgres database. Fully documented example PY file can be found at geoparsepy.example_preprocess_focus_area.py

```python
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
```

# Example code preprocess focus area output (optional)
```
logging started
loading stoplist from /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-geo-stoplist-en.txt
loading whitelist from /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-geo-whitelist.txt
loading blacklist from /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-geo-blacklist.txt
loading building types from /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-buildingtype-en.txt
loading location type corpus /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-buildingtype-en.txt
- 3 unique titles
- 76 unique types
loading street types from /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-streettype-en.txt
loading location type corpus /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-streettype-en.txt
- 15 unique titles
- 32 unique types
loading admin types from /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-admintype-en.txt
loading location type corpus /home/sem/.local/lib/python3.7/site-packages/geoparsepy/corpus-admintype-en.txt
- 14 unique titles
- 0 unique types
loading gazeteer from /home/sem/.local/lib/python3.7/site-packages/geoparsepy/gazeteer-en.txt
starting focus area southampton
starting preprocessing of new focus area : {'focus_area_id': 'southampton', 'admin': ['southampton', 'south east england', 'united kingdom'], 'admin_lookup_table': 'global_cities_admin'}
starting SQL threads
start SQL (point x 2)   .
start SQL (line x 2)   .
start SQL (poly x 2)   .
start SQL (admin x 2)   .
waiting for joins
  . end SQL (admin x 2)   .
  . end SQL (point x 2)   .
  . end SQL (line x 2)   .
  . end SQL (poly x 2)   .
join successful
finished focus area southampton
location id range : {'southampton_point': (1, 1327), 'southampton_line': (1, 2144), 'southampton_poly': (1, 2748), 'southampton_admin': (1, 7)}
```
