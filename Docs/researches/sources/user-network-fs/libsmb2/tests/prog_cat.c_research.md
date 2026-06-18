<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat.c -->
# sources/user-network-fs/libsmb2/tests/prog_cat.c

Purpose: Asynchronous SMB file reader used by cat-related integration tests.

Important APIs, types, and functions: Defines callbacks for disconnect, close, read, open, connect, plus `usage` and `main`. Uses `smb2_connect_share_async`, `smb2_open_async`, `smb2_pread_async`, `smb2_close_async`, and event-loop servicing.

Control flow: After connecting, it opens the URL path read-only, reads chunks at increasing offsets until a zero-length read, writes data to stdout, closes, disconnects, and exits when `is_finished` is set.

State and persistence behavior: Global `is_finished`, 256 KiB buffer, and offset track one transfer. SMB context/URL/handle lifetimes are cleaned at process end.

Dependencies and integration points: Used by `test_0300_cat_basic.sh`, valgrind variant, socket-error variant, and as a model for cancellation test.

Risks: Uses globals, so it supports one operation at a time. Error handling prints messages but returns `rc` initialized to 0 in several failure paths, which may reduce test sensitivity if scripts only check exit status.

Test signals: Covered by basic, valgrind, and socket-error cat shell tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat.c -->
