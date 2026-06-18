# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/inftrees.c

## Purpose
Builds canonical Huffman decode tables for inflate. The single exported function is `inflate_table()`.

## Main API
```c
int inflate_table(codetype type,
                  unsigned short FAR *lens,
                  unsigned codes,
                  code FAR * FAR *table,
                  unsigned FAR *bits,
                  unsigned short FAR *work);
```

Returns:
- `0` on success.
- `-1` for invalid code sets.
- `+1` if the supplied table capacity is insufficient.

## Algorithm
The function:
1. Counts the number of symbols at each bit length.
2. Determines minimum, maximum, and root table bit widths.
3. Checks for over-subscribed or invalid incomplete trees.
4. Sorts symbols by length into `work`.
5. Builds root and sub-tables using bit-reversed deflate canonical-code order.
6. Emits invalid-code markers for unfilled decode entries.
7. Advances `*table` to the next free table slot and updates `*bits`.

## Code Types
Supports:
- `CODES`: code-length alphabet.
- `LENS`: literal/length alphabet with length bases and extra bits.
- `DISTS`: distance alphabet with distance bases and extra bits.

## Important Data
Static base/extra tables define deflate length and distance semantics. The implementation uses `ENOUGH` and `MAXD` from `inftrees.h` to guard dynamic table space.

## Consumers
Used by `inflate.c`, `infback.c`, and fixed-table generation paths.
