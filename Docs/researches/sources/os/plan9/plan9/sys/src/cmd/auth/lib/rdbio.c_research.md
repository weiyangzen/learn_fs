# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/rdbio.c

Reads account biography records from a pipe-delimited file. `rdbio` scans for matching username, clears previous `Acctbio`, and fills post id, full name, department, and up to `Nemail` email fields.

`clrbio` frees all dynamically allocated fields and zeroes the structure.
