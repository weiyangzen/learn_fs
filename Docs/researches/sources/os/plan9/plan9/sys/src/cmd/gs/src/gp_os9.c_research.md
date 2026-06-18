# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_os9.c

Read status: complete.

Purpose: OS-9/OSK-specific Ghostscript platform routines.

Main logic:
- `gp_init` installs `signalhandler` via `intercept`.
- Signal handler clears stdin errors and records interrupt/FPE state in global `interrupted`.
- `gp_do_exit` calls `exit`.
- `gp_get_realtime` uses OS-9 `_sysdate` and `_julian` to compute seconds since January 1, 1980.
- `gp_get_usertime` approximates user time with real time.
- Cache functions are stubs.
- `gp_open_printer` rejects empty names, opens `|command` through `popen`, otherwise opens a file with `rbfopen`.
- `rbfopen` opens a file and sets the `_RBF` raw/binary flag.
- `gp_close_printer` uses `pclose` for pipe targets and `fclose` otherwise.
- Font enumeration functions are stubs.

Filesystem/storage relevance:
- Provides OS-9 printer/file opening and raw/binary file flag handling.

Notable behavior:
- `gp_setmode_binary(FILE *pfile, bool binary)` appears to reference `file->_flag` instead of `pfile->_flag`, which looks like a source-level bug unless hidden by platform macros.
