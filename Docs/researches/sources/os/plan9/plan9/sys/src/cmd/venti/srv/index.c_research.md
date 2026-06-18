# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/index.c

Implements Venti index and index-section initialization, serialization, arena mapping, clump append indexing, and disk lookup helpers.

`initindex()` reads replicated textual index config from an index section, validates configured sections against `ISect` headers, computes bucket divisor state, and maps configured arenas. `newindex()` builds a fresh section map over available section blocks, caps index size below 2^32 buckets, and avoids over-coarse divisors. `wbindex()` writes config to every section and writes each section header.

`initisect()`/`newisect()` load or create an index section, compute bucket capacity and layout offsets, validate block size and ranges, and support version 2 bucket magic. Free functions release section/index state.

`writeiclump()` appends a clump to the first arena with space, computes its index address and `IAddr`, inserts a dirty score into `icache`, and advances `mapalloc`. `amapitoa()` and `amapitoag()` map index addresses back to arenas and arena groups.

Lookup code uses score prefix hashing: `indexsect0()` maps bucket to section, `loadibucket()` loads the responsible bucket, `bucklook()` binary-searches packed sorted entries by score and type, and `loadientry()` checks Bloom first, validates bucket size, and unpacks the matching entry.
