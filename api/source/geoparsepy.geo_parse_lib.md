geoparsepy.geo_parse_lib module
*******************************

Geoparsing is based on named entity matching against OpenStreetMap
(OSM) locations. All locations with names that match tokens will be
selected from a target text sentence. This will result in a set of OSM
locations, all with a common name or name variant, for each token in
the text. Geoparsing included the following features:
   * *token expansion* using location name variants (i.e. OSM multi-
     lingual names, short names and acronyms)

   * *token expansion* using location type variants (e.g. street, st.)

   * *token filtering* of single token location names against WordNet
     (non-nouns), language specific stoplists and peoples first names
     (nltk.corpus.names.words()) to reduce false positive matches

   * *prefix checking* when matching in case a first name prefixes a
     location token(s) to avoid matching peoples full names as
     locations (e.g. Victoria Derbyshire != Derbyshire)

Location disambiguation is the process of choosing which of a set of
possible OSM locations, all with the same name, is the best match.
Location disambiguation is based on an evidential approach, with
evidential features detailed below in order of importance:
   * *token subsumption*, rejecting smaller phrases over larger ones
     (e.g. 'New York' will prefer [New York, USA] to [York, UK])

   * *nearby parent region*, preferring locations with a parent region
     also appearing within a semantic distance (e.g. 'New York in USA'
     will prefer [New York, USA] to [New York, BO, Sierra Leone])

   * *nearby locations*, perferring locations with closeby or
     overlapping locations within a semantic distance (e.g. 'London St
     and Commercial Road' will select from road name choices with the
     same name based on spatial proximity)

   * *nearby geotag*, perferring locations that are closeby or
     overlapping a geotag

   * *general before specific*, rejecting locations with a higher
     admin level (or no admin level at all) compared to locations with
     a lower admin level (e.g. 'New York' will prefer [New York, USA]
     to [New York, BO, Sierra Leone]

Currently the following languages are supported:
   * English, French, German, Italian, Portuguese, Russian, Ukrainian

   * All other languages will work but there will be no language
     specific token expansion available

This geoparsing algorithm uses a large memory footprint, proportional
to the number of cached locations, to maximize matching speed. It can
be naively parallelized, with multiple geoparse processes loaded with
different sets of locations and the geoparse results aggregated in a
last process where location disambiguation is applied. This approach
has been validated across an APACHE Storm cluster.

geoparsepy.geo_parse_lib.calc_OSM_linkedgeodata_uri(tuple_osmid, geom)

   return a linkedgeodata URI for this OSMID (first ID in tuple only)

   Parameters:
      * **tuple_osmid** (*tuple*) -- tuple of OSM IDs that represent
        this location. locations such as roads can have multiple OSM
        IDs which represent different ways along the length of the
        road.

      * **geom** (*str*) -- serialized OpenGIS geometry object e.g.
        'POINT( lon lat )'

   Returns:
      URI to linkedgeodata for first OSM ID in tuple

   Return type:
      str

geoparsepy.geo_parse_lib.calc_OSM_type(dict_osm_tags, dict_geospatial_config)

   calc the OSM tags to work out the type of OSM location. this is
   especialy useful for high level filtering and visualization as OSM
   tags are quite detailed

   Parameters:
      * **dict_osm_tags** (*dict*) -- OSM tags for this location

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geoparse_lib.get_geoparse_config()

   Returns:
      transport | building | admin | other

   Return type:
      str

geoparsepy.geo_parse_lib.calc_OSM_uri(tuple_osmid, geom)

   return a openstreetmap URI for this OSMID (first ID in tuple only)

   Parameters:
      * **tuple_osmid** (*tuple*) -- tuple of OSM IDs that represent
        this location. locations such as roads can have multiple OSM
        IDs which represent different ways along the length of the
        road.

      * **geom** (*str*) -- serialized OpenGIS geometry object e.g.
        'POINT( lon lat )'

   Returns:
      URI to linkedgeodata for first OSM ID in tuple

   Return type:
      str

geoparsepy.geo_parse_lib.calc_best_osm_name(target_lang, dict_osm_tags, dict_geospatial_config)

   return a location name in a target language or best next
   alternative. the default name is the name in the native language of
   the region.

   Parameters:
      * **target_lang** (*str*) -- language code of preference for
        name

      * **dict_osm_tags** (*dict*) -- OSM tags for this location

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

   Returns:
      location name

   Return type:
      unicode

geoparsepy.geo_parse_lib.calc_geom_index(list_data, index_geom=4, index_id=2, index_osm_tag=5)

   compile an index of shapely geoms from a list of data where one
   column is a geom. there can be several geom for each osmid as
   island groups can have a geom per island, but still have a single
   osmid and name (e.g. Shetland, UK). the key for this index will
   either be the original data list row number OR the value from an ID
   column if provided. a OSM tag column can optionally be provided to
   append OSM tag data to the end of the geom index entry, which can
   be useful for determining the location type each geom refers to
   (e.g. admin region, road)

   Parameters:
      * **list_data** (*list*) -- list of data rows where one of the
        column contains a serialized OpenGIS geom

      * **index_geom** (*int*) -- column index in list of data for
        geom

      * **index_id** (*int*) -- column index in list of data for id
        (can be None)

      * **index_osm_tag** (*int*) -- column index in list of data for
        OSM tag dict (can be None)

   Returns:
      dict of { id : [ ( shapely_geom_prepared, shapely_envelope,
      shapely_geom, shapely_representative_point, dict_OSM_tag,
      geom_serialized ), ...] }

   Return type:
      dict

geoparsepy.geo_parse_lib.calc_inverted_index(list_data, dict_geospatial_config, index_phrase=6, index_id=2)

   compile an inverted index from a list of arbirary data where one
   column is a phrase string. the inverted index key is the phrase as
   a tokenized tuple e.g. ('new','york'). the inverted index value is
   an ID value linking back to the original list of data e.g. OSM ID
   tuple or just a row index. | note: the default index values are
   preset for the list of cached locations from
   geo_preprocess_lib.cache_preprocessed_locations()

   Parameters:
      * **list_data** (*list*) -- list of data to create an inverted
        index for e.g. result of
        geo_preprocess_lib.cache_preprocessed_locations()

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

      * **index_phrase** (*int*) -- column index in list_data of
        phrase text to use as a key for inverted index (str/unicode OR
        list/tuple of str/unicode)

      * **index_id** (*int*) -- column index in list_data of an ID
        that the inverted index will point to
        (str/unicode/list/tuple). A value of None will mean the
        list_data row index is used as an ID

   Returns:
      inverted index where key = phrase as a tuple, value = ID value
      for original data list

   Return type:
      dict

geoparsepy.geo_parse_lib.calc_location_confidence(list_loc, dict_geospatial_config, index_token_start=1, index_token_end=2, index_osm_id=5, index_osm_parents=7, index_osm_tags=6, semantic_distance=6, index_geom=4, geom_distance=0.25, index_loc_tokens=3, confidence_tests=1, 2, 3, 4, geom_context=None, geom_cache={})

   calculate confidence values for a set of location matches
   originating from a concatenated set of
   geo_parse_lib.geoparse_token_set() results

   Parameters:
      * **list_loc** (*list*) -- list of locations with geom
        information from geo_parse_lib.create_matched_location_list()

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

      * **index_token_start** (*int*) -- index of matched token start
        position in list_loc

      * **index_token_end** (*int*) -- index of matched token end
        position in list_loc

      * **index_osm_id** (*int*) -- index of OSM ID in list_loc

      * **index_osm_parents** (*int*) -- index of OSM ID of super
        regions to this matches location in list_loc

      * **index_osm_tags** (*int*) -- index of OSM tags in list_loc

      * **semantic_distance** (*int*) -- number of tokens (left and
        right) to look for semantically nearby location checks e.g.
        'London in UK'

      * **index_geom** (*int*) -- index of serialized OpenGIS geom in
        list_loc

      * **geom_distance** (*int*) -- distance for shapely distance
        check (in degrees)

      * **index_loc_tokens** (*int*) -- index of matched loc tokens

      * **confidence_tests** (*int*) -- confidence check tests to run
        when calculating a confidence value. 1 = token subsumption, 2
        = nearby parent region, 3 = nearby locations and nearby
        geotag, 4 = general before specific

      * **geom_cache** (*dict*) -- cache of geom checks with distance
        and intersection results to avoid running the same shapely
        checks twice. this cache will be populated with any new geoms
        that are checked using shapely so might get large over time.
        e.g. dict{ strGeom : [ set(close_tuple_IDs),
        set(not_close_tuple_IDs), set(intersects_tuple_IDs),
        set(not_intersects_tuple_IDs) ] }

   Returns:
      a list of confidence values (0..300) for each location in
      list_loc. locations with a common token can be ranked by
      confidence and the highest value taken. a confidence of 0 means
      the location should be rejected regardless. closeby locations
      scores 2+. super regions present in text scores 10+. geocontext
      intersects location scores 200+ and closeness scores 100+

   Return type:
      list

geoparsepy.geo_parse_lib.calc_multilingual_osm_name_set(dict_osm_tags, dict_geospatial_config)

   return a list of name variants from the OSM tag set for a location.
   this will include the name, alternative and short names,
   abreviations and languages variants

   Parameters:
      * **dict_osm_tags** (*dict*) -- OSM tags for this location

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

   Returns:
      list of name variants for this location

   Return type:
      list

geoparsepy.geo_parse_lib.calc_osmid_lookup(cached_locations)

   create an index of osmid to row indexes in the cached_locations

   Parameters:
      **cached_locations** (*dict*) -- list of cached locations from
      geo_preprocess_lib.cache_preprocessed_locations()

   Returns:
      lookup table mapping an osmid to a set of rows in the cached
      locations (osmids can many entries each with a different geom
      such as island groups)

   Return type:
      dict

geoparsepy.geo_parse_lib.create_matched_location_list(list_match, cached_locations, osmid_lookup)

   create a list of locations based on a set of matches and the
   original cached location table

   Parameters:
      * **list_match** (*list*) -- list of location matches from
        geo_parse_lib.geoparse_token_set()

      * **cached_locations** (*list*) -- list of cached locations from
        geo_preprocess_lib.cache_preprocessed_locations()

      * **osmid_lookup** (*dict*) -- lookup table mapping an osmid to
        a set of rows in the cached locations from
        geo_parse_lib.calc_osmid_lookup()

   Returns:
      list of matched locations with all of the geom information e.g.
      [[<loc_id>, <token_start>, <token_end>, loc_tokens, geom,
      (<osm_id>, ...), {<osm_tag>:<value>}*N_tags, (<osm_id_parent>,
      ...)] ...]

   Return type:
      list

geoparsepy.geo_parse_lib.expand_hashtag(phrase, dict_geospatial_config)

   return a hashtag for a phrase (expects clean phrase text)

   Parameters:
      * **phrase** (*unicode*) -- OSM location phrase to check if it
        makes a good place name

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geoparse_lib.get_geoparse_config()

   Returns:
      hashtag text

   Return type:
      unicode

geoparsepy.geo_parse_lib.expand_osm_alternate_names(tuple_osmid, phrase, dict_osm_tags, dict_geospatial_config)

   return a list of location names expanded to include OSM ref, alt,
   language variants, street and building type variants etc. for
   example 'London St' will generate ['London Street', 'London St'].

   Parameters:
      * **tuple_osmid** (*tuple*) -- tuple of OSM IDs that represent
        this location. locations such as roads can have multiple OSM
        IDs which represent different ways along the length of the
        road.

      * **phrase** (*unicode*) -- cleaned name (not stemmed) of OSM
        location which should be expanded

      * **dict_osm_tags** (*dict*) -- OSM tags for this location

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geoparse_lib.get_geoparse_config()

   Returns:
      list of name variants for this location phrase (including the
      original phrase itself)

   Return type:
      list

geoparsepy.geo_parse_lib.expand_osm_location_types(list_location_names, dict_location_types, dict_osm_tags, dict_geospatial_config)

   given an set of location names return an expanded list with all
   known location type name variants. the original location name will
   always appear in the variant list. e.g. ['london st'] -> [[ 'london
   st', 'london street' ]]

   Parameters:
      * **list_location_names** (*list*) -- list of clean location
        phrase variants for this location (e.g. full name, short name
        and abbreviation)

      * **dict_location_types** (*dict*) -- dict of types prefixes and
        type variants in form { 'title' : listTypePattern, 'type' :
        listTypePattern }. listTypePattern is generated using
        read_location_type_corpus()

      * **dict_osm_tags** (*dict*) -- OSM tags for this location

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geoparse_lib.get_geoparse_config()

   Returns:
      expanded list of location phrase variants

   Return type:
      list

geoparsepy.geo_parse_lib.filter_matches_by_confidence(list_loc, dict_geospatial_config, index_token_start=1, index_token_end=2, index_osm_id=5, index_osm_parents=7, index_osm_tags=6, semantic_distance=6, index_geom=4, geom_distance=0.25, index_loc_tokens=3, confidence_tests=1, 2, 3, 4, geom_context=None, geom_cache={})

   filter a list of matches by match confidence using
   geo_parse_lib.calc_location_confidence() scores. only the highest
   ranked locations for each token will be kept, with the others
   removed from the list

   Parameters:
      * **list_loc** (*list*) -- list of locations with geom
        information from geo_parse_lib.create_matched_location_list().
        this list will be filtered with rows removed that rank low on
        match confidence.

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

      * **index_token_start** (*int*) -- index of matched token start
        position in list_loc

      * **index_token_end** (*int*) -- index of matched token end
        position in list_loc

      * **index_osm_id** (*int*) -- index of OSM ID in list_loc

      * **index_osm_parents** (*int*) -- index of OSM ID of super
        regions to this matches location in list_loc

      * **index_osm_tags** (*int*) -- index of OSM tags in list_loc

      * **semantic_distance** (*int*) -- number of tokens (left and
        right) to look for semantically nearby location checks e.g.
        'London in UK'

      * **index_geom** (*int*) -- index of serialized OpenGIS geom in
        list_loc

      * **geom_distance** (*int*) -- distance for shapely distance
        check (in degrees)

      * **index_loc_tokens** (*int*) -- index of matched loc tokens

      * **confidence_tests** (*int*) -- confidence check tests to run
        when calculating a confidence value. 1 = token subsumption, 2
        = nearby parent region, 3 = nearby locations and nearby
        geotag, 4 = general before specific

      * **geom_cache** (*dict*) -- cache of geom checks with distance
        and intersection results to avoid running the same shapely
        checks twice. this cache will be populated with any new geoms
        that are checked using shapely so might get large over time.
        e.g. dict{ strGeom : [ set(close_tuple_IDs),
        set(not_close_tuple_IDs), set(intersects_tuple_IDs),
        set(not_intersects_tuple_IDs) ] }

   Returns:
      a list of confidence values (0..20) for each location in
      list_loc. locations with a common token can be ranked by
      confidence and the highest value taken. a confidence of 0 means
      the location should be rejected regardless. semantically close
      locations provide scores 1+. geotags inside locations provide
      scores 10+.

   Return type:
      list

geoparsepy.geo_parse_lib.filter_matches_by_geom_area(list_loc, dict_geospatial_config, index_token_start=1, index_token_end=2, index_osm_id=5, index_geom=4, same_osmid_only=False)

   filter a list of matches to favour locations with the largest area
   (e.g. liverpool city border > liverpool admin centre point,
   liverpool city in UK > liverpool suburb in AU). this is helpful to
   choose a single match from a list of matches with same confidence
   as nomrally people are referring to the larger more populated area

   Parameters:
      * **list_loc** (*list*) -- list of locations with geom
        information from geo_parse_lib.create_matched_location_list().
        this list will be filtered with rows removed that do not have
        parents in the region of interest

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

      * **index_token_start** (*int*) -- index of matched token start
        position in list_loc

      * **index_token_end** (*int*) -- index of matched token end
        position in list_loc

      * **index_osm_id** (*int*) -- index of OSM ID in list_loc

      * **index_geom** (*int*) -- index of serialized OpenGIS geom in
        list_loc

      * **same_osmid_only** (*bool*) -- if True limit loc removal to
        same OSMIDs i.e. remove smaller geoms for same OSMID if
        several geoms matched (e.g. admin nodes and city polygons or
        several island polygons)

geoparsepy.geo_parse_lib.filter_matches_by_region_of_interest(list_loc, list_regions_of_interest, dict_geospatial_config, index_osm_parents=7)

   filter a list of matches by region of interest. all locations who
   do not have a parent in the region of interest list will be removed
   from the list

   Parameters:
      * **list_loc** (*list*) -- list of locations with geom
        information from geo_parse_lib.create_matched_location_list().
        this list will be filtered with rows removed that do not have
        parents in the region of interest

      * **list_regions_of_interest** (*list*) -- list of OSM IDs for
        regions of interest

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

      * **index_osm_parents** (*int*) -- index of OSM ID of super
        regions to this matches location in list_loc

geoparsepy.geo_parse_lib.geoparse_token_set(token_set, dict_inverted_index, dict_geospatial_config)

   geoparse token sets using a set of cached locations. no location
   disambiguation is performed here so all possible location matches
   will be returned for each token

   Parameters:
      * **token_set** (*list*) -- list of tokens to geoparse

      * **dict_inverted_index** (*dict*) -- inverted index of cached
        locations from
        soton_corenlppy.common_parse_lib.calc_inverted_index()

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

   Returns:
      list of location indexes for each matched phrase [ [
      (token_start, token_end, set(doc_index1, doc_index2 ...),
      matched_tokens), ... ], ... ]

   Return type:
      list

geoparsepy.geo_parse_lib.get_geoparse_config(**kwargs)

   return a geospatial config object for this specific set of
   languages. the config object contains an instantiated NLTK stemmer,
   tokenizer and settings tailored for the chosen language set. all
   available language specific corpus will be read into memory, such
   as street name variants.  geoparse config settings are below:

      * *lower_tokens* = True, since locations are not alweays
        referenced in text as capitalized Proper Nouns (overrides
        variable keyword args)

      * *building_types* = dict, containing building type name
        variants loaded from each selected language's corpus file

      * *street_types* = dict, containing street type name variants
        loaded from each selected language's corpus file

      * *admin_types* = dict, containing admin region type name
        variants loaded from each selected language's corpus file

      * *gazeteers* = dict, containing local gazateer name variants
        not provided in the OSM database for specific OSM IDs

      * *use_wordnet* = True, remove 1 token location names that
        appear in wordnet with non location meanings

      note: for a list of default config settings see soton_corenlppy.common_parse_lib.get_common_config()
      note: a config object approach is used, as opposed to a global variable, to allow geo_parse_lib functions to work in a multi-threaded environment

   Parameters:
      **kwargs** -- variable argument to override any default config
      values

   Returns:
      configuration settings to be used by all geo_parse_lib functions

   Return type:
      dict

geoparsepy.geo_parse_lib.is_good_place_name(phrase, dict_osm_tags, dict_geospatial_config)

   check if a phrase is a good placename (building, street, admin
   region etc.) for use in text matching. the OSM database contains
   some building names that are really house numbers (e.g. 50) and a
   few basic mistakes which need to be pruned to avoid poor quality
   matches. rejects short names, only numbers, only stoplist names.
   accepts short highway names e.g. 'M3' and multi-token admin
   regions.

   Parameters:
      * **phrase** (*unicode*) -- OSM location phrase to check if it
        makes a good place name

      * **dict_osm_tags** (*dict*) -- OSM tags for this location

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geoparse_lib.get_geoparse_config()

   Returns:
      True if this is a good location name, False if it should be
      rejected for token matching

   Return type:
      bool

geoparsepy.geo_parse_lib.read_location_type_corpus(filename, dict_geospatial_config)

   read a location type corpus containing information for location
   prefix variants (e.g. north london) and location type name variants
   (e.g. london street, london st)

      note : variants are encoded as a list [ [ ('prefix' | 'suffix' | 'both', token, token ... ) ... ], ... ]
         e.g. [ [ ('suffix','clinic'), ('suffix','day','centre') ], [ ('both','uni'),('both','university') ] ]

      corpus file syntax :
         title, ... for location title words not part of the type (e.g. north)
         type, ... for location type types (e.g. hospital)
         # for comments
         +<phrase> = prefix to location name
         <phrase>+ = suffix to location name
         +<phrase>+ = can be both prefix and suffix
         tokens starting with a '*' indicate that the phrase is not to be used for initial match, but will used for expansion variants
         e.g. primary, >>*<<school --> matches only '<name> primary' BUT will expand to '<name> primary', '<name> school' since there are other types of school that could match eroneously

   Parameters:
      * **filename** (*str*) -- filename of location type corpus

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geoparse_lib.get_geoparse_config()

   Returns:
      list of prefix variants and type variants

   Return type:
      list

geoparsepy.geo_parse_lib.reverse_geocode_geom(list_geom, dict_geom_index, dict_geospatial_config)

   reverse geocode a list of OpenGIS geom objects and return all
   indexed geoms that intersect with each geom in this list | note: if
   OSM tag info is specified in the dictGeomIndex then the geom with
   the highest admin level will be returned (i.e. most specific
   location returned, so road before suburb before city before
   country)

   Parameters:
      * **list_geom** (*list*) -- list of serialized OpenGIS geoms to
        geoparse

      * **dict_geom_index** (*dict*) -- geom index from
        geo_parse_lib.calc_geom_index()

      * **dict_geospatial_config** (*dict*) -- config object returned
        from geo_parse_lib.get_geoparse_config()

   Returns:
      a set for each geom checked, with the set containing the ids of
      any intersecting geoms e.g. [ set( tuple_osmid1, tuple_osmid2
      ... ), ... ]

   Return type:
      list
