# sources/user-network-fs/pyfuse3/test/util.py

Purpose: Shared helpers for pyfuse3 tests that need FUSE capability detection, mount readiness, cleanup, and unmount validation.

Important APIs/types/functions: `fuse_test_marker`, `exitcode`, generic `wait_for`, `wait_for_mount`, `cleanup`, and `umount`. `Process` type aliases subprocess and multiprocessing process variants.

Control flow: `fuse_test_marker` checks Darwin shortcut, `fusermount`, `/dev/fuse`, setuid/root conditions, and ability to open `/dev/fuse`, returning either a skip marker or `uses_fuse`. `wait_for_mount` polls `os.path.ismount` and process exit. `cleanup` attempts lazy unmount and terminates/kills process. `umount` performs checked unmount and asserts process exits cleanly.

State and persistence: Acts on external process state and mountpoints. No internal persistent state.

Dependencies and integration points: Used by `test_examples.py` and `test_fs.py`. Depends on platform, `fusermount`, macOS `umount`, subprocess/multiprocessing APIs, and pytest failure/skip mechanisms.

Risks: Lazy unmount may mask cleanup issues. Capability checks are Linux-centric except for Darwin shortcut. Timeouts can fail on overloaded machines or leave processes if kill behavior differs.

Test signals: This file controls whether FUSE tests run and how failures are cleaned, so it is central to test reliability.
