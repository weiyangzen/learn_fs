# sources/test-tools/xfstests-bld/fstests-bld/popt/poptparse.c

Purpose: argv utility layer for popt. It duplicates argv arrays into compact heap storage, parses shell-like strings into argv arrays, and converts simple config files into command-line option strings.

Important functions: `poptDupArgv`, `poptParseArgvString`, and `poptConfigFileToString`.

Control flow: `poptDupArgv` validates argc/argv, computes one allocation containing pointer table plus string data, copies each argument, and returns argc/argv to caller. `poptParseArgvString` tokenizes input using whitespace, single/double quotes, and backslash escaping, grows a temporary argv pointer array, then delegates to `poptDupArgv`. `poptConfigFileToString` reads `name` or `name=value` lines, ignores comments/invalid/missing-value lines, and emits a space-prefixed string of `--name` or `--name="value"` options.

State/persistence: returned argv arrays are heap-owned by the caller and freed as a single block. Temporary parse buffers are freed before return.

Dependencies/integration: used by config parsing and tests. Relies on `_isspaceptr`, `stpcpy`, and popt error codes from `system.h`/`popt.h`.

Risks: `poptParseArgvString` calls `strlen(s)` without NULL guarding. Realloc failure of `argv` loses the old pointer. `poptConfigFileToString` is documented as development-stage, has fixed line buffer length, silently ignores invalid lines, and preserves embedded newlines in quoted values unless stripped by earlier logic.

Test signals: `test-poptrc` alias parsing, `testit.sh` alias/exec tests, and any config-file conversion tests validate quote/escape behavior and single-allocation ownership.
