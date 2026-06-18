# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/fdb.py

Purpose: FoundationDB persistence layer for TestHarness2 coverage and per-test runtime statistics.

Important APIs/types: `str_to_tuple`, `open_db`, `chunkify`, transactional `write_coverage_chunk`, `set_initialized`, `_read_coverage`, public `write_coverage`/`read_coverage`, `TestStatistics`, `Statistics`, and `FDBStatFetcher`.

Control flow: sets FDB API version 630. Coverage writes are chunked by 100 entries, using directory layers for coverage and metadata; before initialization it writes uncovered probes too, later it only increments covered probes. Runtime stats store packed `<II` runtime/run-count values and are read into ordered maps.

State and persistence: caches a global FDB database handle, writes coverage keys under configured Joshua directories, and accumulates runtime statistics in FDB directory subspaces.

Dependencies and integration: external `fdb` Python binding, `fdb.tuple`, `struct`, `Coverage`, `SummaryTree`, and `run.StatFetcher`. Used by `Summary.summarize` and `TestPicker`.

Risks and test signals: API version and cluster availability are environmental; `config.joshua_dir` is asserted for coverage writes; global DB cache ignores cluster-file changes. Test with a local FDB cluster for coverage initialization and stats increment semantics.
