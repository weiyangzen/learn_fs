# sources/test-tools/unionmount-testsuite/tool_box.py

Purpose: shared utility module for unionmount tests. It provides lightweight exceptions, file I/O helpers, shell command execution, kernel taint checking, and overlay option discovery helpers.

Important APIs and functions: defines `ArgumentError`, `TestError`, `exit_error()`, `system()`, `read_file()`, `write_file()`, `write_kmsg()`, `check_not_tainted()`, `check_bool_modparam()`, and `check_bool_mntopt()`.

Control flow: `system` wraps `os.system` and raises on nonzero exit. `current_taint` is captured at import time, and `check_not_tainted` compares later `/proc/sys/kernel/tainted` reads against it. Mount/module option helpers parse sysfs module params and mount option strings.

State and persistence: module global `current_taint` is persistent baseline state. File helpers read/write real system paths such as `/dev/kmsg` and `/sys/module/overlay/parameters`.

Dependencies and integration: imported by setup/unmount/test harness code. Depends on Linux procfs/sysfs, `modprobe`, and Python `os`/`sys`.

Risks: `os.system` uses shell parsing and returns encoded wait status; any nonzero raises a generic `RuntimeError`. `check_not_tainted` constructs a `RuntimeError` with multiple arguments by mistake in the taint mismatch path.

Test signals: helper failures propagate as exceptions, making harness runs fail when shell commands fail or kernel taint changes.
