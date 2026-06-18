# File Research: sources/os/bsd/netbsd-src/lib/libc/cdb/cdbw.c

Build-side writer for NetBSD constant database files. It stores copied key/data pairs, rejects duplicate keys, and emits an `NBCDB` file containing a minimal perfect hash table plus concatenated data.

Key behavior:
- `cdbw_open`, `cdbw_close` manage the writer state, key hash chains, and data arrays.
- `cdbw_put_data` appends copied data blobs and caps total data and counts to 32-bit output limits.
- `cdbw_put_key` hashes keys with `mi_vector_hash`, detects exact duplicates by three hash values plus byte comparison, and grows an internal power-of-two hash table.
- `cdbw_output` builds a 3-uniform hypergraph, repeatedly seeds and peels it until acyclic, assigns `g[]` values, then serializes the database.
- `cdbw_stable_seeder` plus the nbtool fallback division helpers make deterministic host-tool output possible.

Notable details:
- The graph algorithm stores vertex degree and XOR of incident edge ids instead of full incidence lists.
- The generated hash maps a key through three vertices and uses the assigned `g[]` values modulo the data-entry count to recover the data index.
- Output uses little-endian fields and compact 1/2/4-byte tables depending on size.
- Write calls treat short writes as failure rather than retrying.
