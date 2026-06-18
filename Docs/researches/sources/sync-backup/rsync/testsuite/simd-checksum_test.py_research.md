# sources/sync-backup/rsync/testsuite/simd-checksum_test.py

Purpose: smoke/regression test for SIMD rolling/checksum helper implementations. It runs the built `simdtest` tool, which compares accelerated checksum code against the portable C reference.

Important APIs and flow: imports `TOOLDIR`, `test_fail`, and `test_skipped`. The script checks that `TOOLDIR/simdtest` exists and is executable, skips if the build did not produce it, and otherwise runs it with no arguments. Non-zero exit is reported as a test failure.

State and persistence: no source/destination fixture tree and no persistent state beyond process exit status. It depends entirely on the build tree layout and executable bit.

Dependencies and integration: integrates with optional rsync SIMD build features reported by `usage.c` as `SIMD-roll`/`asm-roll`. It is a narrow harness wrapper, not a checksum oracle itself. Main risks are skipped coverage on hosts where SIMD is unavailable and lack of stdout/stderr capture in the success path. Test signal is the helper’s return code.
