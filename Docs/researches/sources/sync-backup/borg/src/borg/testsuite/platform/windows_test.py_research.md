# sources/sync-backup/borg/src/borg/testsuite/platform/windows_test.py

Purpose: Windows-only tests for `SyncFile` creation, text/binary writes, fd fallback, explicit sync, and write-through flag use.

Important APIs and control flow: module-level mark skips non-Windows. Tests write binary and text files through `SyncFile`, require `FileExistsError` for existing target, pass an existing file descriptor from `tempfile.mkstemp` to exercise base fallback behavior, call `.sync()`, and monkeypatch `borg.platform.windows._CreateFileW` to verify `FILE_FLAG_WRITE_THROUGH` in the sixth CreateFile argument.

State and persistence: creates temporary files and mutates Windows platform module function in-process.

Dependencies and integration points: depends on `SyncFile`, Windows-specific platform module constants/functions, pytest, and `tempfile`. It supports durable metadata writes on Windows.

Risks: exact CreateFileW argument position and flag value are Windows implementation details. Existing-file behavior differs from POSIX temp-file replacement flows.

Test signals: persisted file contents, expected existing-file exception, no sync exception, and observed write-through flag.
