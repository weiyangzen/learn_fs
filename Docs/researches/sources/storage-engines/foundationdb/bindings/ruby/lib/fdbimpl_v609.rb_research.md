# sources/storage-engines/foundationdb/bindings/ruby/lib/fdbimpl_v609.rb

Purpose: This compatibility shim restores pre-6.1 Ruby binding APIs for older selected API versions.

Important APIs and types: It aliases `FDB.open` to accept an optional database name, exposes `create_cluster`, defines `ClusterOptions`, and defines `Cluster#open_database`.

Control flow: When loaded for API versions below 610, it wraps `FDB.open` so database names other than `DB` raise error `2013`, and cluster objects delegate opening back to `FDB.open`.

State and persistence behavior: It stores a cluster file path in `Cluster`; no additional persistence is introduced.

Dependencies and integration points: Loaded conditionally by `fdb.rb` after `fdbimpl`. It preserves old binding code that expects clusters and named database calls.

Risks: It deliberately supports only the default database name. Publicly exposing `init` for legacy behavior can widen lifecycle control.

Test signals: Compatibility is covered indirectly by binding tester runs at older API versions and by attempts to open non-default database names.
