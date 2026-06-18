# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/mkhash.c

Builds an on-disk hash sidecar for a given NDB file and attribute. It parses the whole database twice: first to count matching attributes and size an in-memory hash table, then to insert file offsets for matching values.

`enter()` hashes attribute values with `ndbhash()`, stores direct pointers where possible, and creates chained entries using `NDBCHAIN`/`NDBNAP` pointer encoding. The output file is named `file.attribute` and starts with database mtime and hash length followed by the pointer table/chains.

After writing, it verifies the source file’s qid path/version still match the opened database; if the DB changed underfoot it removes the generated hash and exits with `changed`.

Risks include whole-hash memory allocation sized for worst case, pointer-format coupling to NDB macros, and no atomic temporary rename for the generated sidecar.
