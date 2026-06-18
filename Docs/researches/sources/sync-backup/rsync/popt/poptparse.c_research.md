# sources/sync-backup/rsync/popt/poptparse.c

Purpose: Provides argv duplication and string/config-file-to-command-line parsing helpers for popt.

Important APIs, types, and functions: `poptDupArgv()` packs an argv pointer array and copied strings into one malloc block. `poptParseArgvString()` tokenizes a shell-like string into argc/argv with single-quote, double-quote, backslash, and whitespace handling. `poptConfigFileToString()` converts simple key/value config files into a command-line string such as `--name="value"`.

Control flow: `poptParseArgvString()` first builds a temporary argv into a mutable buffer, respecting quote state and escaped characters. It grows the temporary pointer array by `POPT_ARGV_ARRAY_GROW_DELTA`, then normalizes ownership by calling `poptDupArgv()`. `poptConfigFileToString()` reads lines with `fgets()`, skips comments/blanks, parses `name` or `name=value`, trims whitespace, grows the command string, and appends quoted options.

State and persistence behavior: No global state. Returned argv arrays and config strings are heap-owned by the caller. Temporary parsing buffers are freed on exit.

Dependencies and integration points: Uses `system.h` for allocation/string helpers and `_isspaceptr()`. Called by `poptconfig.c` to parse alias/exec replacement argv text and by consumers that accept config-file input.

Risks and test signals: This is intentionally simpler than a full shell parser. Risks include bad quote handling, no escaping of embedded quotes in config values, line length overflow, silently ignored malformed config lines, and integer/memory growth errors. Tests should cover empty input, spaces, quotes, trailing backslashes, long lines, malformed key/value lines, and ownership/freeing of returned argv arrays.
