# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgdbx.c

- Role: Berkeley DB hash implementation of the `Msgdb` interface.
- Key behavior: Opens a DB hash with 2 MiB cache, stores counts as 4-byte big-endian values, deletes keys for nonpositive counts, enumerates with `seq`.
- Integration: Backing store for token/class databases.
- Risks/notes: `mdopen(nil, 1)` relies on `dbopen` behavior for unnamed/temp DBs; values larger than 32 bits are truncated.
