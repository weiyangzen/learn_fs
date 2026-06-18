# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/mkhash.c

Builds an on-disk hash sidecar for an ndb file attribute.

Key elements:
- Usage: `mkhash file attribute`.
- Opens the requested ndb file and finds the matching `Ndb` object.
- Counts matching attribute occurrences to size the hash table.
- Builds an in-memory hash table using `ndbhash`, `NDBPUTP`, chain flags, and fixed pointer lengths.
- Writes `<file>.<attribute>` with mtime/hash length header and hash entries.
- Verifies the source file did not change underneath by checking qid path/version after writing.

Notable behavior:
- Allocates enough for worst-case chaining.
- Fails if database offsets exceed `NDBSPEC`.
- Creates the hash file with `DMTMP|0664`.

Risks and quirks:
- The typo `"not enougth memory"` is the literal exit string.
- If source changes during build, the generated hash file is removed.
