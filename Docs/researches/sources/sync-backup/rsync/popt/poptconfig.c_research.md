# sources/sync-backup/rsync/popt/poptconfig.c

Purpose: Implements popt configuration file loading and alias/exec registration. It reads files, expands optional glob path lists, validates config file sanity, parses individual config lines, and initializes a context with user-specified config paths.

Important APIs, types, and functions: `poptSaneFile()` rejects null names, rpm backup/new files, non-regular files, and executable files. `poptReadFile()` reads an entire file into a NUL-terminated buffer and can trim escaped newlines. `poptReadConfigFile()`, `poptReadConfigFiles()`, and `poptReadDefaultConfig()` are the main loaders. `poptInit()` wraps `poptGetContext()` plus `poptReadConfigFiles()`. Internal helpers include `glob_pattern_p()`, `poptGlob()`, `configAppMatch()`, and `poptConfigLine()`.

Control flow: `poptReadConfigFiles()` splits colon-separated paths, expands globs, sanity-checks each match, and calls `poptReadConfigFile()`. `poptReadConfigFile()` reads and line-normalizes the file, skipping comments and blank lines before passing entries to `poptConfigLine()`. A line supplies app name, `alias` or `exec`, option token, and argv text. File-backed option text can be interpolated, parsed by `poptParseArgvString()`, stripped of `--POPTdesc=`/`--POPTargs=` metadata, and added through `poptAddItem()`.

State and persistence behavior: Successful config entries mutate `con->aliases` or `con->execs`. Default config checks `/etc/popt`, `/etc/popt.d/*`, and `$HOME/.popt` when present. The implementation intentionally returns success for each config line at exit, which makes malformed lines non-fatal after local cleanup.

Dependencies and integration points: Uses `system.h`, `poptint.h`, POSIX file APIs, optional `glob.h`/`fnmatch.h`, and `poptparse.c`. Config aliases later appear in help via `popthelp.c` and are used by the parser core.

Risks and test signals: Risks include whole-file memory use, silent bad-line acceptance, glob/platform differences, path sanity policy gaps, and `errno = -EOVERFLOW` oddness on oversized files. Tests should cover config comments, escaped newlines, app-name glob matching, metadata stripping, missing files, unsafe files, and default config discovery.
