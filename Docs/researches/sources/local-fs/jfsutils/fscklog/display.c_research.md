# File Research: sources/local-fs/jfsutils/fscklog/display.c

Implements display of an already extracted JFS fsck service log.

Key contents:
- Defines `_JFS_XCHKDMP` before including headers to limit unnecessary includes.
- Uses global `local_recptr`, `file_name`, and shared `xchklog_buffer`.
- Entry point `xchkdmp()` initializes input-buffer fields, sets highest fsck message number, opens input file, dumps log records, and closes input.
- `open_infile()` selects default `fscklog.new` or `fscklog.old` if no filename was specified, opens file for reading, reads the first `XCHKLOG_BUFSIZE` buffer, and verifies the 16-byte `jfs_chklog_eyecatcher`.
- `dump_service_log()` iterates over extracted `chklog_entry_hdr` records, validates `entry_length` against remaining buffer bytes, prints message text directly, and refills the buffer until EOF.
- `xchkdmp_fscklog_fill_buffer()` reads more extracted-log bytes from the file and resets buffer offset.
- `xchkdmp_final_processing()` closes the input stream.

Interactions:
- Displays the extraction format written by `extract.c`, not raw on-device fsck log records.
- Uses message sending for format/open/read errors.

Research notes:
- `printf(msg_txt)` prints extracted log text as the format string. If extracted log contents are untrusted, this is a format-string risk.
- The display logic depends on valid record lengths to stay aligned and handles invalid lengths by stopping the current buffer.
