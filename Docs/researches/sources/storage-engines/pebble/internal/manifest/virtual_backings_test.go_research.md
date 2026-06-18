<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings_test.go -->
# sources/storage-engines/pebble/internal/manifest/virtual_backings_test.go

Purpose: datadriven tests for `VirtualBackings`, exercising state transitions and panic paths through a compact command language under `testdata/virtual_backings`.

Important APIs/functions: `TestVirtualBackings` creates a fresh `MakeVirtualBackings` for each test file and interprets commands `add`, `remove`, `add-table`, `remove-table`, `protect`, and `unprotect`. It builds minimal `TableBacking` and virtual `TableMetadata` values with scanned `n`, `size`, `table`, `blobValueSize`, and `level` args.

Control flow and state: every datadriven command executes under a `defer` that converts panics into output strings, allowing fixture coverage for invalid transitions. Successful commands return `bv.String()`, so expected files assert backing counts, stats, unused ordering, table lists, protection counts, and heap printouts.

Dependencies and integration: uses `github.com/cockroachdb/datadriven`, `base.DiskFileNum`, `base.TableNum`, and package-local manifest types. The tests do not exercise remote placement because all added backings use `base.Local`; remote-specific stats and exclusion from the rewrite heap remain weaker signals. Risk coverage is strong for command-level state transitions but depends on fixture breadth for heap ordering and panic wording.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings_test.go -->
