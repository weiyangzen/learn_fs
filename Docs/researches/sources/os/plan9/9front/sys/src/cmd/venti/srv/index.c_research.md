# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/index.c

`index.c` implements Venti’s persistent score-to-arena-address index. It initializes existing indexes from section config tables, creates new index maps, validates section geometry, serializes index metadata, and maps logical arena addresses back to `Arena` objects.

The lookup path hashes the top score bits into a bucket, uses the bloom filter before disk reads, loads the owning index section block, validates bucket bounds, then binary-searches sorted packed `IEntry` records by score and disk type. The write path stores clumps in arenas through `writeiclump()`, constructs `IAddr`, inserts index entries, and advances arena allocation under `ix->writing`.

Important integration points are `loadibucket()`, `bucklook()`, `ientrycmp()`, `amapitoa()`, and `wbindex()`. The file is central to correctness: section maps must be contiguous, bucket divisor math must match `2^32` key-space coverage, and bucket entries must stay sorted for binary lookup and index rebuild tooling.
