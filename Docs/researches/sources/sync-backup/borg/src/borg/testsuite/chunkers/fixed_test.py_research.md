<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_test.py

Purpose: pytest tests for fixed-size chunking over sparse and nonsparse files plus slow fuzz reconstruction.

Important APIs: `ChunkerFixed`, `cf`, `cf_expand`, `make_sparsefile`, `make_content`, sparse maps, `BS`, and `pretty_print`.

Control flow: parametrized sparse test creates real files for each sparse map/header/sparse-mode combination, chunks them with `ChunkerFixed(BS, header_size, sparse)`, and compares normalized chunks with expected content. Slow fuzz reconstructs random, all-same, and all-zero data for several block/header sizes.

State and persistence: writes temporary sparse files and uses real filesystem behavior.

Dependencies/integration: depends on test sparse maps being aligned to fixed chunk size and on helper representation of holes/allocated zeros. Risks include filesystem sparse behavior, header handling across block boundaries, and slow test cost. Test signals are exact normalized chunk comparisons and reconstructed byte equality.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/chunkers/fixed_test.py -->
