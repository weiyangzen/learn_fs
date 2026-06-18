# sources/user-network-fs/samba/source4/client/cifsddio.c

## Purpose
Implements the concrete I/O backends for Samba's `cifsdd` utility: POSIX file descriptor access, SMB/CIFS file access, and the block-buffer fill/flush helpers used by the dd-style copy loop. The file turns local paths or UNC paths into a common `struct dd_iohandle` with `io_read`, `io_write`, and `io_seek` callbacks.

## Important APIs, types, and functions
- `struct fd_handle` embeds `struct dd_iohandle` and stores a local `fd`; `IO_HANDLE_TO_FD()` relies on the embedded handle being at offset zero.
- `struct cifs_handle` embeds `struct dd_iohandle`, owns an `smbcli_state`, an SMB file number, and a logical offset.
- `open_fd_handle()` opens local files with `O_DIRECT` and `O_SYNC` when requested by `DD_DIRECT_IO` and `DD_SYNC_IO`, and with read or write/create flags from `DD_WRITE`.
- `init_smb_session()` calls `smbcli_full_connection()` with global command-line credentials, loadparm context, resolver, tevent context, SMB options, session options, and GENSEC settings.
- `open_smb_file()` issues `RAW_OPEN_NTCREATEX`, maps cifsdd options into access, create disposition, write-through/no-buffering flags, share access, and optional oplock request.
- `dd_open_path()` chooses local I/O if `file_exist(path)` is true, otherwise parses UNC paths with `smbcli_parse_unc()` and opens SMB, falling back to local open for non-UNC paths.
- `dd_fill_block()` and `dd_flush_block()` implement the copy buffer contract and update global `dd_stats`.

## Control flow
Local reads/writes call `read()`/`write()` once per requested block and return the actual byte count. SMB reads/writes build raw READX/WRITEX unions and maintain the current offset in `struct cifs_handle`; `smb_seek_func()` only updates that cached offset. Opening a CIFS path first creates a session, then opens the remote file, then returns the embedded generic handle.

The buffering helpers are higher-level. `dd_fill_block()` keeps appending `block_size` reads until the caller's buffer has `need_size` bytes or reaches EOF. `dd_flush_block()` writes either a requested partial block or as many full blocks as fit, counts full/partial output blocks, and moves any remainder to the start of the buffer for the next copy iteration.

## State and persistence behavior
Persistent external state is limited to local files and remote SMB files. In-memory state includes file descriptors, SMB session handles, SMB fnums, offsets, `DD_END_OF_FILE` in the handle flags, and global `dd_stats`. There is no close/destructor path in this file, so ownership and cleanup are expected from surrounding cifsdd code or process teardown.

## Dependencies and integration points
The file depends on Samba's `libcli` raw SMB client, command-line credential/loadparm globals, resolver and tevent contexts, and definitions from `cifsdd.h` such as `dd_iohandle`, `DD_*` flags, `PROGNAME`, and `dd_stats`. It integrates with `cifsdd.c` as the device abstraction layer and with `test_cifsdd.sh` for blackbox local/remote copy coverage.

## Risks and edge cases
- `dd_open_path()` treats any existing local path as local even if the string resembles a UNC path, and missing local paths that are not UNC are opened as local, which may surprise callers.
- `open_cifs_handle()` logs a missing share-relative path but does not immediately return after the error message.
- SMB offset advancement asserts against integer wrap for reads but not writes.
- `open_smb_file()` returns `-1` on failure, but `open_cifs_handle()` still returns a handle with that fnum; later I/O will fail rather than open failing atomically.
- The direct-I/O block-size alignment requirements are delegated to the caller and platform.

## Test signals
`test_cifsdd.sh` exercises local-to-local, local-to-remote, remote-to-local, and remote-to-remote copies over block sizes `512`, `4k`, and `48k`, then validates with `cmp`. That gives broad blackbox coverage of the path selection and fill/flush behavior, but not explicit error handling, partial writes, direct/sync I/O, oplocks, or invalid UNC handling.
