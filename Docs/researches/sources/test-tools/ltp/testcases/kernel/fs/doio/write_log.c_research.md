# sources/test-tools/ltp/testcases/kernel/fs/doio/write_log.c

Purpose: implements a compact appendable write-history log for doio-style writes, including support for later overlaying completion state for asynchronous operations and scanning records backward.

Important APIs/types/functions: `wlog_open`, `wlog_close`, `wlog_record_write`, `wlog_scan_backward`, `wlog_rec_pack`, `wlog_rec_unpack`, `struct wlog_file`, `struct wlog_rec`, `struct wlog_rec_disk`, `Wlog_Error_String`, `WLOG_REC_MAX_SIZE`, and `WLOG_STOP_SCAN`.

Control flow: `wlog_open` opens one append descriptor and one random-access descriptor. `wlog_record_write` packs fixed fields plus optional path/host/pattern strings; appends full records with a two-byte trailing length when `offset < 0`, or overlays only the fixed portion at a saved offset for completion updates. `wlog_scan_backward` reads blocks from EOF toward BOF, uses the trailing length field to locate complete records, unpacks into `wlog_rec`, and invokes a caller callback until count/EOF/stop.

State/persistence behavior: persists variable-length binary records in the log file named by `wfile->w_file`. Error state is a global static string. File descriptors remain owned by the `wlog_file` handle until `wlog_close`.

Dependencies/integration: consumed by doio write-verification paths that need to reason about which patterns should be present in a target file after a stress run. Depends on POSIX `open`, `write`, `lseek`, `read`, `close`, `umask`, and the disk layout declared in `write_log.h`.

Risks/test signals: record lengths are stored in two bytes, so layout and `WLOG_REC_MAX_SIZE` must stay bounded. Overlay callers must save valid offsets. Reverse scanning is sensitive to corrupt length trailers. Test signal is successful callback traversal; failures return `-1` and populate `Wlog_Error_String`.
