# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/updatedb.c

Read status: complete, 214 lines.

`replica/updatedb` scans a tree described by a proto file, compares it to a replica database, writes change log records, and optionally updates the database.

It logs additions (`a`), content changes (`c`), metadata changes (`m`), and deletions (`d`). It can emit only changes, only log output, choose root/proto, override uid, seed timestamp/sequence values, and exclude paths.

`walk` compares current `Dir` metadata with database state. After `rdproto`, `main` walks unmarked database entries and logs/removes deletions unless `-c` changes-only mode is active. `warn` treats suspected network or I/O errors as fatal to avoid logging mass deletions caused by failed remote reads.

Filesystem relevance: central scanner for generating replica update logs and maintaining client/server metadata state.
