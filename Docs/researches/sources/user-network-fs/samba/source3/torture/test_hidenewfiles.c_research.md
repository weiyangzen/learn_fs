# sources/user-network-fs/samba/source3/torture/test_hidenewfiles.c

Purpose: This file tests Samba's "hide new files timeout" behavior. It verifies that a newly created unreadable file is hidden from directory listings until the configured timeout has elapsed, while containing directories remain visible.

Important APIs/types/functions: `servertime()` creates and deletes a temporary file to obtain server-side creation time. `have_file_fn()` and `have_file()` list the share with `cli_list()` and test whether a name is visible. Public entrypoints are `run_hidenewfiles()` and `run_hidenewfiles_showdirs()`.

Control flow: `run_hidenewfiles()` opens a connection, removes stale test files, creates `new_hidden.txt`, records its last-write time, then loops: list for visibility, fetch current server time by creating `timestamp.txt`, compute age, and sleep until the file becomes visible. It fails if the file appears before five seconds or remains hidden past ten times that interval. `run_hidenewfiles_showdirs()` creates `dir/x.txt` and immediately verifies that `dir` itself is visible.

State/persistence behavior: Remote files and directories are created on the test share. `new_hidden.txt` is marked delete-on-close in cleanup. `servertime()` uses `FILE_DELETE_ON_CLOSE` for the timestamp probe. The behavior depends on server-side timestamps and smb.conf's hide-new-files configuration.

Dependencies and integration points: The file depends on torture SMB connection helpers, `cli_ntcreate()`, `cli_list()`, `cli_unlink()`, `cli_mkdir()`, `cli_rmdir()`, security access masks, and NT time conversion. It integrates with VFS/share configuration for hiding newly created files.

Risks: The code hard-codes `hideunreadable_seconds = 5` with a comment saying this is configured in smb.conf. Mismatch between configuration and test constant causes false failures. Server/client clock conversion and directory listing filters are also important.

Test signals: Passing requires no early listing visibility for `new_hidden.txt`, eventual visibility within the allowed bound, and immediate visibility of the parent directory in the showdirs case.
