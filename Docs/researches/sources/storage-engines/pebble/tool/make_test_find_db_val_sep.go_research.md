## sources/storage-engines/pebble/tool/make_test_find_db_val_sep.go

Purpose: build-tagged generator for a value-separation DB fixture used by `find` tests, especially blob-reference handling.

Important APIs/types/functions: `minSizeForValSep` sets the value-separation minimum to three bytes. Local `db` wraps `*pebble.DB`; methods parse Cockroach-formatted keys with `cockroachkvs.ParseFormattedKey`, set values, flush, and close. `main` configures `KeySchema`, `KeySchemas`, `FormatValueSeparation`, small block sizes, and a `ValueSeparationPolicy`.

Control flow: the generator removes `tool/testdata/find-val-sep-db`, opens a DB with value separation enabled, writes several keys with values above and below the minimum, flushes, writes more keys and flushes, then writes thirty additional keys and flushes again.

State and persistence: writes a fixture DB containing SSTables, blob files, WALs, OPTIONS, and MANIFEST state under the testdata directory.

Dependencies and integration: uses Cockroach key schema/comparer support, `blobtest` import presence, Pebble value separation, and VFS. The fixture supports `find --load-blobs` and key-schema-aware formatting.

Risks: relative path and Pebble format behavior determine output. The `blobtest.Values` field is unused. If value-separation thresholds or file layout change, fixtures and expected datadriven output must be regenerated.

Test signals: ensures `find` can encounter blob references, map blob files through manifests/catalog data, and optionally load separated values for matching keys.
