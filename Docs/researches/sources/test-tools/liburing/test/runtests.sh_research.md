# sources/test-tools/liburing/test/runtests.sh

Purpose: main shell harness for running selected liburing test binaries with timeout, optional device arguments, dmesg scanning, skip/fail/timeout aggregation, and timing history.

Important APIs/types/functions: Bash arrays and associative arrays, `TIMEOUT`, `TEST_FILES`, `TEST_MAP`, optional `config.local`, `_check_dmesg()`, `run_test()`, `timeout -s INT -k`, `/dev/kmsg`, `dmesg`, status code `77` for skip, `TEST_EXCLUDE`, and `TEST_GNU_EXITCODE`.

Control flow: sources `config.local` if present and validates mapped devices. For each requested test, it optionally runs once without a device, against each `TEST_FILES` device, or against a specific `TEST_MAP` entry. `run_test()` prints status, skips excluded tests, runs the binary under timeout, preserves core files, checks exit/skips/xfails, scans dmesg after a marker, and records elapsed seconds under `output/`.

State/persistence behavior: writes timing files in `output/`, may move `core` to `core-$test_name`, may create `.dmesg` files for kernel warnings, and reads local config. No checklist state is modified.

Dependencies/integration: integrates compiled test binaries, kernel log access when root, system `timeout`, optional block devices, and liburing convention that `77` means skipped.

Risks/test signals: dmesg pattern matching can produce root-only signals and may be noisy if markers are unavailable. Timeout status is reported but not treated as failure unless downstream policy interprets output.
