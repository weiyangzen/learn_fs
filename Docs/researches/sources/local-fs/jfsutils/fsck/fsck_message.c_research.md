# File Research: sources/local-fs/jfsutils/fsck/fsck_message.c

This module centralizes fsck message emission and fsck log recording. It defines global `msg_lvl`, initially `fsck_debug`, and `dbg_output`, initially disabled. It uses the global aggregate fsck record `agg_recptr` for log-buffer state.

`fsck_record_msg()` appends a formatted message string to the in-memory fsck log buffer when logging is active. It skips logging if the log is full, unavailable, or allocation failed. It creates an `fscklog_entry_hdr`, copies the text into a fixed-size local `log_entry`, appends a null terminator, pads the entry to a 4-byte boundary, writes a full buffer out with `fscklog_put_buffer()` when needed, clears the buffer after flushing, swaps the log-entry header on big-endian machines, and copies the entry into the fsck log buffer. It updates `fscklog_last_msghdr` and `fscklog_buf_data_len`.

`v_fsck_send_msg()` is the varargs backend for fsck message macros. It indexes `msg_defs[msg_num]`, formats the message text with `vsnprintf`, builds a debug suffix from `basename(file_name)` and `line_number`, prints the message if `message->msg_level <= msg_lvl`, optionally prints source-location detail when `dbg_output` is set, appends the debug detail to the logged string, and calls `fsck_record_msg()`.

The file uses `_GNU_SOURCE` for `basename()`, includes `fsck_message.h`, `fsckwsp.h`, endian helpers, and `xfsckint.h`. It bridges user-visible stdout diagnostics and persistent fsck log records.

Important implementation detail: `msg_string` is bounded, but `fsck_record_msg()` uses `strncpy()` followed by `strlen(msg_txt)` to advance `entry_length`. If an oversized input ever reached it, length accounting would rely on the original string length rather than the truncated copy. In current use, `v_fsck_send_msg()` formats into a smaller bounded buffer before calling it, which constrains normal callers.
