# sources/test-tools/unionmount-testsuite/tests/noent-creat-excl.py

Purpose: tests missing-file creation with `O_CREAT|O_EXCL` across read/write/append modes.

Important APIs/types/functions: five `subtest_*` functions using `ctx.open_file`.

Control flow: creates a new file on first open, writes `q` for write-like modes, verifies content, then repeats the exclusive open expecting `EEXIST` and verifies content remains unchanged.

State and persistence: creates upper files and optional one-byte data.

Dependencies and integration: uses context creation tracking and open flag mapping.

Risks: exact behavior for `O_CREAT|O_EXCL|O_RDONLY` is Linux-specific but expected by the suite.

Test signals: catches overlayfs mistakes where exclusive create overwrites or alters existing upper files.
