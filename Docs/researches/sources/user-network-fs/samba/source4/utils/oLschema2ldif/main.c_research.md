<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/main.c -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/main.c

## Purpose

This file implements the `oLschema2ldif` command-line tool. It parses options, opens input/output streams, initializes an LDB context and base DN, runs the converter library, and prints a conversion summary.

## Important APIs, Types, and Functions

- `usage()` prints help text and exits.
- `options` stores `--basedn`, `--input`, and `--output`.
- `main()` uses Samba popt helpers, `ldb_init()`, `ldb_dn_new()`, stream opening, `process_file()`, and cleanup.

## Control Flow

`main()` allocates a top-level talloc context, sets `LDB_URL=NONE`, builds a popt context, rejects invalid options, requires `--basedn`, initializes default stdin/stdout streams and an LDB context, validates the base DN, optionally opens input and output files, calls `process_file()`, closes streams, prints `"Converted %d records with %d failures"`, frees the popt context, and exits with status `0`.

## State and Persistence Behavior

The only persistent output is the optional LDIF output file. The tool also writes the summary to stdout even when stdout is the LDIF output stream, so callers redirecting LDIF to stdout get the summary appended after LDIF output.

## Dependencies and Integration Points

It depends on the converter library, Samba command-line/popt helpers, LDB DN parsing, and standard C file streams. The build script links it as `oLschema2ldif` with manpage `oLschema2ldif.1`.

## Risks and Edge Cases

The manpage synopsis omits the required `--basedn` option even though the program requires it. Error handling calls `usage()` and exits rather than returning distinct error codes. `fclose(copt.in)` and `fclose(copt.out)` are called even when they are stdin/stdout.

## Test Signals

Pass signals are option parsing, rejection of missing/malformed base DN, successful conversion from file or stdin, output file creation when requested, and accurate conversion summary counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/main.c -->
