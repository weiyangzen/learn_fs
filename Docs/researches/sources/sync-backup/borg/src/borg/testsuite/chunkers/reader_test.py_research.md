<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/reader_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/reader_test.py

Purpose: unit tests for sparse map detection, `FileReader`, and `FileFMAPReader` blockification/allocation behavior.

Important APIs: `sparsemap`, `FileReader`, `FileFMAPReader`, `Chunk`, `make_sparsefile`, `fs_supports_sparse`, sparse maps, `BS`, and allocation constants.

Control flow: `coalesce_sparse_map` models OS coalescing. Sparsemap tests create real sparse files and compare `sparsemap` results via file handle and file descriptor. `FileReader` tests cover simple reads, multiple reads, and reading from a mocked FMAP reader with mixed chunks. `FileFMAPReader` tests cover empty/small/multiple reads, zero-block detection as `CH_ALLOC`, explicit maps for data and holes, partial map seeking, all-zero allocation types, real sparse file behavior with sparse on/off, and default `_build_fmap`.

State and persistence: mostly `BytesIO`; sparse tests create temporary real sparse files and use `os.open` descriptors.

Dependencies/integration: depends on `SEEK_HOLE`/`SEEK_DATA`, chunk allocation metadata, zero-block detection, reader timing attribute compatibility, and default huge data map size `2**62`. Risks include OS-specific sparse reporting, accidental hole/allocation conflation, and partial fmap seek errors. Test signals are exact chunk data/allocation/size assertions and expected sparse maps.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/reader_test.py -->
