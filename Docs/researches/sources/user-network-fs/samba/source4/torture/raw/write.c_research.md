# sources/user-network-fs/samba/source4/torture/raw/write.c

## Purpose
`write.c` is the raw SMB1 write torture suite. It verifies legacy write variants (`SMBwrite`, `SMBwriteX`, write-unlock, write-close), data integrity, bad handles, locked regions, sparse/large-file offsets, and one deliberately malformed SMB write request.

## Important APIs, types, and functions
The suite entry point is `torture_raw_write()`. Test cases are `test_write()`, `test_writex()`, `test_writeunlock()`, `test_writeclose()`, and `test_bad_write()`. Helpers are `setup_buffer()` and `check_buffer()`, which produce deterministic pseudo-random data from a seed. It uses `union smb_write`, `union smb_fileinfo`, `smb_raw_write()`, `smbcli_read()`, `smbcli_lock()`, `torture_set_sparse()`, `smbcli_request_setup()`, `smbcli_request_send()`, `smbcli_request_receive()`, and raw packet field writers.

## Control flow
Each write-variant test creates `\testwrite\test.txt`, allocates a 90 KB buffer, performs a zero-length write, writes small and large buffers, reads data back, and compares deterministic content. `test_write()` covers basic `RAW_WRITE_WRITE` and a near-4 GB offset when `CAP_LARGE_FILES` is set. `test_writex()` additionally verifies write mode values, lock conflict behavior by manipulating the session PID around a write lock, and optionally probes offsets from `2^33` up to `2^63` when dangerous mode is enabled. `test_writeunlock()` verifies that write-unlock writes data but requires a matching lock to return success, returning `RANGE_NOT_LOCKED` otherwise. `test_writeclose()` confirms the write closes the handle, so repeated use returns `INVALID_HANDLE`, then reopens to verify contents and large offsets. `test_bad_write()` manually constructs an `SMBwrite` with an impossible length and accepts `INVALID_PARAMETER` or `UNSUCCESSFUL`.

## State and persistence behavior
State is temporary file content, file size, sparse-file state, byte-range locks, and handle validity under `\testwrite`. The deterministic random buffer avoids storing fixtures. Large-offset tests can create sparse logical sizes far beyond the physical write size. Each test removes the directory and exits the raw session during cleanup.

## Dependencies and integration points
The file depends on negotiated server capabilities (`CAP_LARGE_FILES`, `lockread_supported`), torture settings (`dangerous`, `writeclose_support`), raw write marshalling, lock handling, sparse-file setup, and pathinfo `ALL_INFO` size queries. It exercises both high-level raw APIs and low-level SMB request construction.

## Risks and edge cases
Dangerous writex can probe extremely large offsets and should remain opt-in. `srandom()`/`random()` global state makes helper output deterministic but process-global. Large sparse writes depend on filesystem/server support and can be skipped. Some tests call `torture_skip()` after resources have been opened, relying on harness behavior. The malformed write test validates error tolerance but can expose disconnect behavior on strict servers.

## Test signals
Passing signals are exact byte counts, byte-for-byte readback of pseudo-random data, zero-filled gaps before offset writes, `INVALID_HANDLE` on bad or closed handles, `FILE_LOCK_CONFLICT` on locked writex regions, `RANGE_NOT_LOCKED` for write-unlock without locks, correct `ALL_INFO.size` after large writes, and accepted error codes for malformed write length.
