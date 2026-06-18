# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkindex.c

Command-line checker comparing current on-disk index and Bloom filter against a freshly built sorted entry list.

Key behavior:
- Builds expected raw sorted index entries with `sortrawientries`.
- `checkindex` streams expected entries with `IEStream`, builds expected buckets with `buildbucket`, and compares each bucket to the live index.
- When zero checking is enabled, verifies empty buckets too.
- `checkbucket` reads an on-disk bucket, compares expected versus actual entries, and prints extra, missing, or wrong-address entries.
- `checkbloom` compares old and newly built Bloom filters, reports extra/missing bits, and with `-f` replaces the old filter.
- CLI supports `-B blockcachesize`, `-f`, and `-Z` to skip zero-bucket checking.

Interactions:
- Depends on `buildbuck.c`, `bloom.c`, `dcache.c`, and raw index sorting from elsewhere in the server.
- Uses a temporary partition argument to hold sorted entries.

Notable details:
- Error counters distinguish spurious entries, missing entries, and address mismatches.
- `/* ZZZ make buffer size configurable */` notes fixed 64 KiB stream buffer.
