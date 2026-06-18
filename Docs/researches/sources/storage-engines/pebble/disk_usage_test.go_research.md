# sources/storage-engines/pebble/disk_usage_test.go

## Purpose
`disk_usage_test.go` validates the disk-usage estimation APIs in `disk_usage.go`, including closed-DB behavior and datadriven scenarios involving local, remote, external, ingested, flushed, and compacted files.

## Important APIs, types, and functions
`TestEstimateDiskUsageClosedDB` opens an in-memory DB, writes a key, closes it, and asserts both `EstimateDiskUsage` and `EstimateDiskUsageByBackingType` panic after close. `TestEstimateDiskUsageDataDriven` interprets `testdata/disk_usage` commands. It supports `open`, `close`, `batch`, `flush`, `build`, `ingest`, `build-remote`, `ingest-external`, `compact`, `estimate-disk-usage`, and `estimate-disk-usage-by-backing-type`.

## Control flow, state, and persistence
The datadriven test maintains a shared in-memory filesystem, a remote in-memory storage object, and a current `*DB`. The `open` command resets any existing DB and configures `FormatExciseBoundsRecord`, disables automatic compactions, and installs a simple remote-storage factory with an external locator. Build and ingest commands create local, remote, or external SSTables through shared Pebble test helpers. Estimate commands default to range `a` through `z` unless two command arguments provide explicit start and end keys.

For backing-type estimates, the test checks the returned hierarchy before printing it: external usage must be less than or equal to remote usage, and remote usage must be less than or equal to total usage. Compaction commands return the LSM state after compacting, allowing expected files and placement behavior to be encoded in the datadriven output.

## Dependencies and integration points
The file depends on `leaktest`, `datadriven`, `remote.NewInMem`, `remote.MakeSimpleFactory`, `vfs.NewMem`, and `require`. It also depends on test helpers defined elsewhere for parsing DB options, defining batches, building SSTables, ingesting local/remote/external files, compacting, and rendering the LSM.

## Risks and invariants
The test assumes closed DB methods should panic rather than return errors, matching the core DB closed-state convention. The datadriven parser uses positional command arguments for ranges, so malformed test input can accidentally fall back to defaults or produce unexpected ranges. Since size estimates are approximate, expected output must tolerate implementation-defined estimates where partial overlap or blob-reference scaling changes. Remote and external storage setup must match object-provider placement semantics for the hierarchy assertions to remain meaningful.

## Test signals
The strongest signal is coverage across local, remote, and external placement plus compaction and ingestion. The tests do not directly assert exact behavior for `fileCache.estimateSize` errors or WAL-exclusion behavior, so those remain residual risk areas.
