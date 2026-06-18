# File Research: sources/local-fs/jfsutils/libfs/logform.h

This header declares the log formatting API:

- `int jfs_logform(FILE *, int, int, uint, int64_t, int, uuid_t, char *);`

It is protected by `H_LOGFORM` and is included by `logredo.c` for extendfs recovery log reformatting. The parameters correspond to the target device, aggregate block sizing, filesystem flags, inline-log start/length, optional external-log UUID, and optional label.

Note: the closing comment says `H_LORFORM`, a harmless typo.
