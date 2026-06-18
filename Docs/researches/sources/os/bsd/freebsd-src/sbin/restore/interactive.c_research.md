# File Research: sources/os/bsd/freebsd-src/sbin/restore/interactive.c

Purpose: implements `restore -i`, an interactive shell for browsing dump contents and choosing files to extract.

Key functions:
- `runcmdshell()` dispatches commands: `add`, `cd`, `delete`, `extract`, `ls`, `pwd`, `quit`/`xit`, `verbose`, `setmodes`, `what`, and `Debug`.
- `getcmd()` parses input, handles multiple arguments over repeated calls, canonicalizes paths, and expands globs.
- Custom glob hooks `rst_opendir`, `glob_readdir`, `rst_closedir`, and `glob_stat` make globbing operate against dump directory contents rather than the live filesystem.
- `canon()` normalizes names to restore’s `./...` convention and removes duplicate slashes, `.`, and `..`.
- `printlist()`, `mkentry()`, `formatf()`, and `fcmp()` implement an `ls`-style listing with restore-specific markers.
- `onintr()` uses `setjmp`/`longjmp` to recover to the prompt on interrupt in interactive mode.

Integration: uses directory APIs from `dirs.c`, selection callbacks from `restore.c`, and symbol-table state from `symtab.c`. It triggers actual extraction by calling `createfiles()`, `createlinks()`, and `setdirmodes()`.

Risk notes: command parsing uses static buffers and manual quote/backslash handling. `canon()` assumes enough destination capacity after an explicit length check, but later transformations still rely on fixed-size buffers. Interrupt handling is non-local and depends on global shell state.
