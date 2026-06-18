# sources/user-network-fs/samba/source3/client/clitar.c

## Purpose
`clitar.c` implements the `smbclient` tar extension when Samba is built with libarchive. It bridges the interactive and command-line tar commands to SMB client operations so users can create an archive from a remote share or extract a local/archive stream into a remote share. Without libarchive the same public entry points compile as stubs that report tar support is unavailable.

## Important APIs, Types, And Functions
- `struct tar` is the central mutable context. It owns a talloc context, operation and selection modes, block size, hidden/system/incremental/reset/dry/regex/verbose flags, byte counters, archive path, selection path list, libarchive handle, and file/directory counters.
- `tar_ctx` is the global context used by `client.c` interactive commands and exposed through `tar_get_ctx()`.
- `cmd_block()`, `cmd_tarmode()`, and `cmd_tar()` are interactive command handlers. They read `cmd_ptr`, update `tar_ctx`, or parse and immediately execute a tar operation.
- `tar_parse_args()` parses tar flag strings and positional values, configures `struct tar`, reads inclusion files for `F`, updates the global `newer_than` variable for `N`, and marks the context ready with `to_process`.
- `tar_process()` dispatches to `tar_create()` or `tar_extract()`, then clears process state and frees context-owned paths.
- `tar_create()`, `tar_create_from_list()`, `get_file_callback()`, and `tar_get_file()` implement SMB-to-archive traversal and transfer.
- `tar_extract()` and `tar_send_file()` implement archive-to-SMB extraction.
- `tar_create_skip_path()`, `tar_extract_skip_path()`, `tar_path_in_list()`, `is_subpath()`, and path helpers implement inclusion/exclusion and DOS/Unix path normalization.

## Control Flow
The normal create path starts with `tar_parse_args()` choosing `TAR_CREATE`, a selection mode, an archive path, and optional path filters. `tar_process()` calls `tar_create()`, which opens a libarchive writer unless in dry-run mode. Include mode with explicit paths calls `tar_create_from_list()`, temporarily changing the client current directory for nested masks. Otherwise it lists from `client_get_cur_dir()` with `do_list()`. Each `do_list()` item reaches `get_file_callback()`, which builds a clean remote path, skips `.` and `..`, evaluates `tar_create_skip_path()`, and calls `tar_get_file()`. `tar_get_file()` builds a PAX archive entry, optionally clears the archive bit, opens remote regular files with `cli_open()`, reads with `cli_read()`, and writes data to libarchive.

The extract path opens the archive from a filename or stdin, iterates headers with `archive_read_next_header()`, evaluates `tar_extract_skip_path()`, and calls `tar_send_file()`. `tar_send_file()` converts archive paths to DOS-style remote paths, creates parent directories with `make_remote_path()`, opens or truncates the remote file with `cli_open()`, writes each libarchive data block using `cli_writeall()`, closes the file, and applies mode/mtime with `cli_setatr()`.

## State And Persistence
Most per-operation state is stored in `tar_ctx` and its child talloc context, then released after `tar_process()`. The command also mutates process-global Samba client state: it reads and changes the current remote directory during include traversal, writes to the local tar file or stdout, reads from stdin or a local archive, creates remote directories/files, writes file contents, sets remote attributes, and may unset the remote archive bit when reset mode is active. `tar_set_newer_than()` writes the external `newer_than` filter used by smbclient listing logic.

## Dependencies And Integration Points
This file integrates with libarchive, Samba client listing and I/O APIs (`do_list`, `cli_open`, `cli_read`, `cli_writeall`, `cli_close`, `cli_setatr`, `cli_chkpath`, `cli_mkdir`), `client_get_cur_dir()`/`client_set_cur_dir()`, Samba talloc and debug helpers, and DOS attribute constants. It depends on `source3/include/client.h` for `struct file_info` and on generated client prototypes for external command/listing APIs.

## Risks
- `cmd_tarmode()` appears to invert verbose/noverbose table values: `verbose` sets false and `noverbose` sets true, which is likely behavioral drift from intended UI text.
- `tar_create_skip_path()` ignores include-list filtering during create because include mode traversal starts from listed paths. This is intentional for explicit include mode but means include-mode path checks differ from extraction path checks.
- Path handling is security-sensitive. `fix_unix_path()` removes simple leading prefixes, but extraction still depends on `client_clean_name()` and server path semantics for traversal edge cases.
- `tar_send_file()` skips non-regular and non-directory entries, so symlinks, devices, fifos, ACLs, owners, and extended attributes are not restored.
- `cli_setatr()` receives archive mode bits and mtime; mapping POSIX mode to SMB attributes may be lossy or server-dependent.
- The fallback build stubs keep symbols available, but any caller expecting `tar_get_ctx()` to be non-NULL must tolerate the non-libarchive build.

## Test Signals
Useful tests include argument parsing for mutually exclusive operations/selections, `b`, `N`, `F`, dry-run and stdin/stdout paths; create/extract round trips with nested directories, hidden/system/archive attributes, path lists, exclude patterns, case-insensitive subpath matching, and filenames using slash/backslash forms; no-libarchive builds; failed SMB open/read/write/close paths; and extraction attempts containing `../` or absolute paths.
