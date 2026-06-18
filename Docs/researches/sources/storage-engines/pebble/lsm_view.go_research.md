# sources/storage-engines/pebble/lsm_view.go

Purpose: this file builds a shareable LSM visualization URL for a live `DB`. It translates the current manifest version and selected table details into `internal/lsmview.Data`, then asks the visualization package to encode it into a URL.

Important APIs/types/functions: `DB.LSMViewURL` references the current version under `DB.mu`, constructs an `lsmViewBuilder`, populates levels and keys, builds data, and returns either the generated URL or an error string. `lsmViewBuilder` holds comparer/formatter state, level names, table metadata, sorted key labels, and a scan threshold flag. `InitLevels`, `PopulateKeys`, `Build`, and `tableDetails` perform the conversion.

Control flow: `InitLevels` emits L0 sublevels from newest/display-top order, falls back to an empty `L0`, then appends L1+. `PopulateKeys` collects every table smallest/largest user key, sorts and compacts with the configured comparer, and formats labels. `Build` determines whether table contents should be scanned; up to 100 tables it opens iterators for point keys, range deletions, and range keys to include sample contents. `tableDetails` emits table number, key bounds, size, virtual/backing information, seqnums, synthetic prefix/suffix, point samples, range deletions, and range-key spans with caps on displayed entries.

State and persistence behavior: the method takes a version reference and releases it after building. It opens iterators only for display details and closes them via `CloseAll`. It performs no DB mutation and persists nothing except the returned URL string.

Dependencies and integration points: integrates with manifest table metadata, object-provider lookup for virtual table backing, `tableNewIters`, SSTable iterators, `humanize`, comparer formatting, and `internal/lsmview.GenerateURL`. It is a diagnostics/debugging entry point.

Risks and test signals: scanning is capped by table count and per-detail row limits, but opening many tables can still be nontrivial. Errors are embedded in returned strings/details rather than propagated, matching a diagnostic API. Risk areas include virtual object lookup, nil custom key formatters, iterator close handling, and range-key metadata display.
