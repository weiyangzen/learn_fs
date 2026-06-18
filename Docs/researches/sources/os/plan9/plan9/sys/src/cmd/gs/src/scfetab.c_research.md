# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/scfetab.c

Static encoding tables for Ghostscript’s `CCITTFaxEncode` filter, also used by `scfdgen.c` to generate decode tables.

It defines:

- EOL code `cf_run_eol`.
- 1-D uncompressed marker `cf1_run_uncompressed`.
- 2-D pass, vertical, horizontal, and uncompressed codes.
- Group 3 2-D EOL codes distinguishing 1-D and 2-D rows.
- White run termination and makeup tables.
- Black run termination and makeup tables.
- Uncompressed run and exit code tables.
- Dummy `scfetab_dummy`.

This file is table data for CCITT fax image compression. It is not filesystem code.
