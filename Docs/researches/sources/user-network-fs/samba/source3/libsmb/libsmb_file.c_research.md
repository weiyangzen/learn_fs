# sources/user-network-fs/samba/source3/libsmb/libsmb_file.c

Purpose: implements regular-file operations for libsmbclient, plus shared attribute get/set helpers used by stat, chmod, utimes, and other file/directory APIs.

Important APIs: `SMBC_open_ctx()` parses an SMB URL, obtains `SMBCSRV`, resolves DFS path, opens a file with `cli_open()` or `cli_ntcreate()` for `O_PATH`, records `targetcli`, and adds an `SMBCFILE` to `context->internal->files`. `SMBC_creat_ctx()` wraps open. `SMBC_read_ctx()`, `SMBC_write_ctx()`, `SMBC_splice_ctx()`, `SMBC_lseek_ctx()`, `SMBC_ftruncate_ctx()`, and `SMBC_close_ctx()` validate the open-file list and delegate to `cli_*`. `SMBC_getatr()` and `SMBC_setatr()` implement attribute/stat translation and fallback paths.

Control flow and state: each open file tracks `cli_fd`, original URL, owning `SMBCSRV`, current offset, file/dir flag, and DFS-resolved `targetcli`. Reads/writes update `file->offset`; append mode seeks to EOF once after open. `SMBC_getatr()` tries `cli_qpathinfo2`, then `cli_qpathinfo3`, then old `cli_getatr()` if NT SMBs are unavailable, caching unsupported pathinfo levels in `SMBCSRV`. `SMBC_setatr()` prefers `cli_setpathinfo_ext()` and falls back to open plus `cli_setattrE()`/`cli_setatr()`.

Dependencies and integration: depends on `SMBC_parse_path`, `SMBC_server`, DFS `cli_resolve_path`, `setup_stat`, context options such as share mode and POSIX extensions, and `SMBC_dlist_contains` for handle validation.

Risks: `O_APPEND` is approximated by one seek at open, so concurrent appends may not be strict. Pathinfo capability flags are per server and reset on complete failure. Error conversion differs between read/write paths (`cli_status_to_errno` vs `map_errno_from_nt_status`). Tests should cover invalid context/file handles, DFS target persistence across read/write/close, POSIX SMB3.11 open flag toggling, append seek failure cleanup, fallback stat/setattr behavior, and failed close purging.
