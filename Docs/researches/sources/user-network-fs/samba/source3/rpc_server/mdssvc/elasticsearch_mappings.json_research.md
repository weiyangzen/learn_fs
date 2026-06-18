# sources/user-network-fs/samba/source3/rpc_server/mdssvc/elasticsearch_mappings.json

## Purpose
This JSON file is mdssvc's default translation table from macOS Spotlight metadata attributes and content type identifiers to Elasticsearch query fields. It lets the Spotlight query parser turn client-side metadata predicates into backend-specific Lucene query fragments.

## Important APIs, Types, And Functions
The top-level keys are `attribute_mappings` and `mime_mappings`. Each attribute mapping maps a Spotlight key to a `type` consumed by `enum ssm_type` (`bool`, `num`, `str`, `fts`, `date`, or `type`) plus an Elasticsearch `attribute` field path. The wildcard `"*"` maps to full-text search. Content-type mappings translate numeric or UTI-like Spotlight type values such as `public.jpeg`, `public.text`, and `public.archive` to one or more MIME patterns.

## Control Flow
At runtime `es_parser_test.c` or mdssvc loads the JSON with Jansson. `es_map_sl_attr()` looks up a Spotlight attribute under `attribute_mappings`, converts the string `type` into an `ssm_type`, and escapes the target Elasticsearch field name. `map_type()` uses `mime_mappings` to expand Spotlight type values into MIME query alternatives.

## State And Persistence
This file is static configuration data. It does not persist runtime state, but changing it changes server query behavior after reload or next load. Samba configuration can override the path through the `elasticsearch:mappings` parameter.

## Dependencies And Integration Points
The mapping format is coupled to `es_mapping.c`, `es_mapping.h`, and `es_parser.y`. It assumes Elasticsearch indexed documents expose fields like `content`, `file.content_type`, `file.last_modified`, `file.filename`, `attributes.owner`, `path.real`, and `meta.raw.*`.

## Risks And Test Signals
Risks include stale field names relative to the Elasticsearch index schema, incorrect owner/group mappings, missing attributes causing query failure unless unknown attributes are ignored, and overly broad MIME expansions. Test signals include JSON parse validation, parser conversions for every listed metadata key, type expansion tests for UTI and numeric values, wildcard full-text searches, and integration tests against a representative Elasticsearch index.
