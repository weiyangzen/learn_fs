# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/pack.c

Big-endian packing and unpacking for fossil on-disk structures.

It serializes/deserializes `Header`, `Label`, `Entry`, and `Super`, validates header/super magic and versions, checks label state invariants, and maps local disk addresses to pseudo-global scores. `Entry` packing stores local entries differently from Venti entries, preserving local tag, snapshot epoch, and archive flag in fields not used by global scores.

These routines define the persistent disk layout consumed by the formatter, cache, fs, and standalone tools.
