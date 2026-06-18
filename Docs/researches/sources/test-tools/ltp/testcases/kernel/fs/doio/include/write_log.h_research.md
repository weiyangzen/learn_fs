# sources/test-tools/ltp/testcases/kernel/fs/doio/include/write_log.h

Purpose: `write_log.h` defines the write-log record format and API used by `doio.c` to persist enough metadata for later corruption reconstruction and backward scanning. It separates an in-memory user record from a compact on-disk bitfield record plus variable-length path, host, and pattern data.

Important APIs and types: constants include `WLOG_MAX_PATH`, `WLOG_MAX_PATTERN`, `WLOG_MAX_HOST`, `WLOG_REC_MAX_SIZE`, `WLOG_STOP_SCAN`, and `WLOG_CONTINUE_SCAN`. `struct wlog_rec` is the caller-facing record with pid, offset, byte count, open flags, completion flag, async flag, host, path, and pattern fields plus lengths. `struct wlog_rec_disk` is the packed on-disk header with bitfields. `struct wlog_file` carries append and random-access file descriptors plus the log path. Public functions are `wlog_open()`, `wlog_close()`, `wlog_record_write()`, and `wlog_scan_backward()`, with `Wlog_Error_String` exported for diagnostics.

Control flow role: the header has no implementation, but it defines the protocol used by `doio.c`: append a preliminary record before a write with `w_done = 0`, then rewrite or append completion information after the write with `w_done = 1` at the saved log offset. Backward scans use the two-byte record length stored at the end of each on-disk record.

State and persistence behavior: write logs are durable files. Each on-disk record stores fixed metadata, variable path/host/pattern bytes without null terminators, and a trailing two-byte total length to support reverse traversal. `struct wlog_file` persists open descriptors while logging or scanning. The path, host, and pattern maximums bound record size and must remain synchronized with bitfield widths.

Dependencies and integration points: `doio.c` uses the API when `-w` is enabled. Comments reference `doio_check`, which reconstructs file extents and distinguishes completed from uncertain writes by `w_done`. The format is also platform-sensitive through CRAY vs non-CRAY offset bit widths.

Risks: bitfield layout, width, and endian behavior are compiler/platform sensitive, so log files are not a robust cross-architecture interchange format. The non-CRAY disk offset bitfield is 32 bits, limiting logged offsets. `uint` is defined as a macro if absent, which can conflict with other headers. Size constants require manual synchronization with bit widths. Fixed host/path/pattern limits can truncate or reject long metadata depending on implementation.

Test signals: coverage should create/truncate/open logs, record incomplete and complete writes, scan backward across multiple records, validate maximum path/host/pattern lengths, and confirm `doio_check` can interpret both completed and interrupted write records.
