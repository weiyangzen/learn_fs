# sources/test-tools/xfstests-bld/fstests-bld/popt/poptconfig.c

Purpose: implements popt config-file support and convenience initialization. It reads config files, parses application-specific alias/exec declarations, expands globbed config paths, checks file sanity, and wires config-defined items into a `poptContext`.

Important functions: `poptSaneFile`, `poptReadFile`, `poptReadConfigFile`, `poptReadConfigFiles`, `poptReadDefaultConfig`, `poptInit`, and `poptFini`. Private helpers include `poptGlob`, `configAppMatch`, and `poptConfigLine`.

Control flow: `poptReadConfigFiles` splits colon-delimited path lists, optionally applies `@` sanity checks, expands globs, and calls `poptReadConfigFile`. File reading can trim escaped newlines. `poptReadConfigFile` builds logical lines, skips comments/blank lines, and sends each line to `poptConfigLine`. A config line must match the current app name, specify `alias` or `exec`, identify an option or file-backed option, parse replacement argv with `poptParseArgvString`, strip `--POPTdesc`/`--POPTargs` metadata, then call `poptAddItem`.

State/persistence: aliases and exec entries are persisted inside `con->aliases`/`con->execs`. File buffers and glob arrays are temporary. Default config reads from configured sysconfdir, `/etc/popt`, `/etc/popt.d/*`, and `$HOME/.popt`.

Dependencies/integration: uses `glob`, `fnmatch`, `stat`, `open/read/lseek`, environment `HOME`, `POPT_SYSCONFDIR`, parser APIs in `poptparse.c`, and item insertion in `popt.c`.

Risks: `poptSaneFile` appears inverted or at least surprising: it returns `1` for stat failure and for regular owner-owned files that are not group/world writable, while several comments say `0 on OK`. `poptConfigLine` forcibly returns success even after parse failures, hiding invalid lines. Config files can define exec aliases, so trust boundaries are important. Globs and `@` sanity behavior are subtle and should be tested with real permissions.

Test signals: `test-poptrc.in`, `test1.c`, and `testit.sh` verify aliases, execs, `--POPTdesc`, `--POPTargs`, default config via `HOME`, and alias argument substitution.
