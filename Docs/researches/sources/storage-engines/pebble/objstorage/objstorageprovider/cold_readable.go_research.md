<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_readable.go -->
## sources/storage-engines/pebble/objstorage/objstorageprovider/cold_readable.go

Purpose: implements a readable wrapper for cold-tier objects whose metadata suffix has been copied to a hot local file for cheaper small metadata reads.

Important APIs and types: `newColdReadableWithHotMeta` constructs `coldReadableWithHotMeta`. The wrapper implements `objstorage.Readable`. `coldReadHandle` implements `objstorage.ReadHandle` over the same split-storage behavior.

Control flow: reads with offsets before `metaStartOffset` go to the wrapped cold readable. Reads entirely in the metadata suffix go to `readMetaAt`, which lazily opens the hot metadata file once via `sync.Once`. Reads that span both regions are conservatively served from cold storage because the full object exists there. Read handles ignore read-before optimization for metadata and create a cold read handle with `NoReadBefore`.

State and persistence: stores the cold readable, metadata FS/path/start offset, and lazily opened metadata file/error. Closing closes both cold and hot files if opened.

Dependencies and integration: used by the object storage provider's cold-tier path. Depends on `objstorage`, `vfs`, and `firstError` from provider utilities.

Risks and edge cases: split reads are not optimized and go cold. Hot metadata open errors are cached by `sync.Once`; transient open failures persist for the wrapper lifetime. `RecordCacheHit` clips reports to the cold portion only.

Test signals: no direct listed tests; cold-tier provider tests elsewhere would be expected to cover sidecar metadata reads.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/objstorageprovider/cold_readable.go -->
