# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/buildbuck.c

Purpose: build index buckets from a sorted stream of packed index entries.

Key structures and behavior:
- `IEStream` tracks a partition-backed stream of packed `IEntry` records: read offset, remaining entries, buffer, current position, and end position.
- `initiestream` allocates the stream and buffer.
- `freeiestream` frees stream resources.
- `peekientry` keeps at least one packed `IEntry` available by compacting unread bytes and reading more from the partition.
- `iebuck` computes the bucket number from score hash bits and index divisor.
- `buildbucket` fills an `IBucket` with consecutive stream entries belonging to one bucket, merges duplicate score/type entries by preferring the larger address, checks max bucket data size, and advances the stream.

Integration points:
- Used by Venti index-building code.
- Depends on packed `IEntry` layout having score first, plus `hashbits`, `ientrycmp`, `unpackientry`, and `IBucket`.

Risks:
- Duplicate handling mutates the in-buffer entry when preferring the older larger address path; this is compact but subtle.
- Bucket overflow returns `TWID32` and sets an error.
- Correct bucket grouping assumes input entries are sorted consistently with bucket/hash order.
