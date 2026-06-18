# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/buildbuck.c

Provides stream-to-bucket assembly for sorted packed index entries.

Key behavior:
- Defines opaque `IEStream`, a buffered stream over sorted packed `IEntry` records stored on a `Part`.
- `initiestream` records partition, offset, remaining entry count, and allocates the read buffer.
- `peekientry` refills the buffer, preserving partial records, and returns the current packed `IEntry`.
- `iebuck` maps a packed score to an index bucket via `hashbits(score, 32) / ix->div`.
- `buildbucket` consumes consecutive entries for the same bucket into an `IBucket`, detects duplicate score/type entries, and keeps the one with the larger arena address.

Interactions:
- Used by `checkindex.c` to build expected buckets from sorted raw entries.
- Depends on packed `IEntry` layout where score is first.

Notable details:
- Duplicate index entries set an expected-operation error and choose the larger address as likely newer/correct.
- Returns `TWID32` on end/error/overflow.
