# Nominatim

## Search queries in Nominatim
The search API allows you to look up a location from a textual description or address. Nominatim supports structured and free-form search queries.

### Endpoint
```
https://nominatim.openstreetmap.org/search?<params>
```

For our purposes, the free-form query will be appropriate, since we do not have enough data from Sanudo's index to create a structured query.

#### Free Form Queries
Free-form queries are processed first left-to-right and then right-to-left if that fails. Commas are optional, but improve performance by reducing the complexity of the search.

### Output

Output format is one of xml, json, jsonv2, geojson, geocodejson. Default is ```jsonv2```.

We may want to limit the maximum number of returned results.

We may want to show the language of results (set the preferred language order to Italian and English).

We may want to include some boost parameters to give a preference to results that limit the search to country of Italy, etc.

# Extra Information
OSM Objects
-------
Three types of elements in OpenStreetMap: nodes, ways, and relations.