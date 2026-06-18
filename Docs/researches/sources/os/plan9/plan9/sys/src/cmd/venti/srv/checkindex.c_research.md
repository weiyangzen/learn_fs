# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkindex.c

Implements `checkindex`, which rebuilds a sorted expected index stream from arenas into a temporary partition, then compares expected buckets against the on-disk index.

`checkbucket()` loads the actual bucket from the correct `ISect`, compares packed entries in sorted order, and reports missing, extra, and wrong-address entries. `checkindex()` uses `IEStream` and `buildbucket()` to generate expected buckets and can also check zero/empty buckets unless `-Z` is used.

`checkbloom()` compares the live Bloom filter with a freshly generated one, counting spurious and missing bits. With `-f`, it writes the rebuilt Bloom filter back when needed; otherwise missing bits are fatal.

The command loads the Venti config, optional existing Bloom filter, initializes enough disk cache for arenas and index sections, builds raw sorted entries with `sortrawientries()`, and fails if index or Bloom discrepancies remain.
