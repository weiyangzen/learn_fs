# sources/user-network-fs/samba/source4/torture/libsmbclient/libsmbclient.c

## Purpose
This large smbtorture module validates the public `libsmbclient` C API: context lifecycle, configuration setters, URL parsing, directory enumeration, file operations, metadata, xattrs, no-anonymous behavior, rename semantics, and SMB3 POSIX extension behavior.

## Important APIs, types, and functions
`torture_libsmbclient_init_context()` creates and configures an `SMBCCTX` with command-line workgroup/user, auth callback, debug settings, and optional client protocol. Pure API tests cover `smbc_version`, `smbc_new_context`, `smbc_init_context`, `smbc_setLogCallback`, `smbc_setConfiguration`, basic getters/setters, and many `smbc_setOption*`/`smbc_getOption*` pairs. Network tests use `smbc_opendir`, `smbc_readdir`, `smbc_readdirplus`, `smbc_readdirplus2`, `smbc_getdents`, `smbc_telldir`, `smbc_lseekdir`, `smbc_creat`, `smbc_open`, `smbc_close`, `smbc_unlink`, `smbc_mkdir`, `smbc_rmdir`, `smbc_stat`, `smbc_fstat`, `smbc_utimes`, `smbc_rename`, `smbc_getxattr`, and `smbc_fgetxattr`.

## Control flow
The module registers many simple tests under the `libsmbclient` suite. Some tests are local API checks; others require `torture:smburl`. Directory tests create temporary files, enumerate shares or directories, verify returned entries, test seeking back to saved directory offsets, and compare `readdir`, `getdents`, `readdirplus`, `readdirplus2`, and `stat` results. Metadata tests verify `utimes`, missing-file `ENOENT`, xattr sizing, and POSIX extension xattrs. The POSIX hardlink test opens a prepared file and checks its POSIX stat info reports three hardlinks.

## State and persistence behavior
The suite creates and deletes files and directories on the configured SMB share, including `test_readdirplus.txt`, `rd_seek` with 100 files, `src`, `dst`, `getxattr`, and POSIX fixture paths. `smbc_setConfiguration()` temporarily mutates process-global loadparm settings and restores the default config file afterward. Context state is process-local and freed per test.

## Dependencies and integration points
The file depends on `<libsmbclient.h>`, command-line credentials, loadparm globals, dynamic config paths, SMB protocol constants, and smbtorture helpers. It integrates with actual SMB server behavior through `torture:smburl` and with POSIX extension support through SMB3 xattrs.

## Risks and edge cases
Many tests require a writable share and sufficient credentials. Directory-order seeking assumes an open handle's in-memory list remains stable. The rename test documents a prior SMB2 overwrite bug. POSIX tests require a server/share prepared with POSIX extensions and a file with expected hardlink count. Some cleanup paths free contexts but do not always close every possible handle after early assertion failures.

## Test signals
Passing tests provide broad confidence that libsmbclient context APIs work, network file operations round-trip correctly, directory cursor APIs are consistent, stat metadata matches `readdirplus2`, xattr behavior reports sizes and errors properly, anonymous fallback can be disabled, and SMB3 POSIX extension metadata is exposed.
