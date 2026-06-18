# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/msgclass.c

- Role: Classifies token-count input against Berkeley DB-backed class databases and optionally trains the winning database.
- Control flow: Reads token files/stdin into an in-memory `Msgdb`, locks optional lockfile, opens class DBs, computes informative-word probabilities, prints class probabilities and keyword evidence, then updates class counts when `-a` is set.
- Key functions: `noteword`, `process`, `lockfile`.
- Integration: Uses `msgdb.h` and `msgdbx.c`.
- Risks/notes: The source contains an apparent syntax error in `lockfile`: `if(strstr(err, "file is locked")==nil && strstr(err, "exclusive lock")==nil))` has an extra `)`.
