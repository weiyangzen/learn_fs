# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/msgdbx.c

This file implements `Msgdb` using Plan 9’s Berkeley-style `dbopen()` hash database interface.

Values are stored as four-byte big-endian counts. `mdget()` returns zero for missing or malformed values. `mdput()` deletes entries for nonpositive counts or stores the encoded count otherwise. `mdenum()` resets iteration, and `mdnext()` uses `db->seq()` to return token/count pairs.

The database is opened read-write, optionally with `OCREATE`, using a 2 MB cache size.
