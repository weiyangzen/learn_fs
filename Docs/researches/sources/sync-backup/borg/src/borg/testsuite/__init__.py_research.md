# sources/sync-backup/borg/src/borg/testsuite/__init__.py

Purpose: provides shared test-suite utilities and platform capability probes used across Borg's tests. It is intentionally lightweight enough for `borg.selftest`, so pytest is optional and many helpers are pure stdlib wrappers.

Important APIs/types/functions: module constants expose FUSE availability, nanosecond timestamp precision, filesystem feature flags, and rejected `..` path cases. `same_ts_ns` compares timestamps within platform granularity. `granularity_sleep` waits long enough for filesystem timestamp changes, including a Windows ctime tunneling workaround. `unopened_tempfile`, `changedir`, `is_root`, `are_symlinks_supported`, `are_hardlinks_supported`, `are_fifos_supported`, `is_utime_fully_supported`, `is_birthtime_fully_supported`, and `filter_xattrs` are reused fixtures/helpers. `BaseTestCase` maps unittest assertions to old Borg naming. `FakeInputs` simulates repeated `input()` calls.

Control flow: platform capability booleans are computed at import time or via `functools.lru_cache`. Capability probes create temporary paths, attempt the operation, verify observable metadata, and return False on unsupported OS errors. Timestamp granularity is derived from Python/posix build flags and OS overrides. `FakeInputs.__call__` prints a prompt if given and pops a queued answer, raising `EOFError` when exhausted.

State and persistence behavior: all filesystem writes occur in temporary directories created by `tempfile`; lru-cached probes persist results in-process to avoid repeated expensive feature checks. `granularity_sleep` intentionally affects test timing but writes no state. `filter_xattrs` removes SELinux and Apple provenance attributes from comparisons because those can be injected by the host environment.

Dependencies and integration points: imports Borg FUSE implementation flags, platform abstraction, platform flags, and standard OS/stat/sysconfig/tempfile APIs. It is imported by archive and archiver tests for skip conditions, filesystem setup, timestamp assertions, and xattr filtering.

Risks: import-time probing of flags and FUSE metadata can be sensitive to unusual filesystems. Cached capability results assume the temp filesystem represents the test workspace. Windows ctime workaround can add a 15 second sleep when requested. Optional pytest import means `BaseTestCase.assert_raises` can be either pytest's `raises` or unittest's context manager.

Test signals: this file is mostly infrastructure; signals come from downstream tests being stable across Linux, macOS, Windows, BSD, FUSE, fakeroot, and filesystems with different timestamp/xattr behavior.
