# sources/sync-backup/casync/test/fuzz/fuzz-main.c

Purpose: standalone runner for fuzz targets outside libFuzzer.

Important APIs/types/functions: `main` reads input files from argv, loads their bytes, and invokes the target entry point declared in `fuzz.h`.

Control flow/state: iterates over command-line paths, opens/reads each test case into memory, calls `LLVMFuzzerTestOneInput`, then exits nonzero on I/O/allocation failures.

Dependencies/integration: lets Meson tests or developers replay corpus entries without a fuzzing engine. Paired with `fuzz-compress.c` and optional generated corpora.

Risks/test signals: whole-file loading can be memory-heavy for very large inputs; replay coverage depends on passing representative corpus files.

Source research group: `subset-b-009122`.
