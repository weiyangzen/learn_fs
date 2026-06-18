# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/gb.h

## Role

`gb.h` declares the shared interface for Plan 9 `tcs` GB encoding conversion support. It defines the size and indexing convention for `tabgb`, which is implemented in `gb.c`.

## Contents

The header documents that GB byte pairs range from `0xA1A1` to `0xF7FE` inclusive and are mapped with a “kuten-like” ordinal scheme to `101..8794`.

It defines:

```c
#define GBMAX 8795
```

and declares:

```c
extern long tabgb[GBMAX];
```

The comment on `tabgb` states that it stores runes indexed by GB ordinal.

## Consumers

`gb.c` includes this header to size and define `tabgb`.

`conv_gb.c` includes it to translate GB input byte pairs into runes and to build a reverse rune-to-GB table for output.

`font/gmap.c` includes it via `../gb.h` to map rune ranges back to GB ordinals for font tooling.

## Contract Notes

The `GBMAX` value is one greater than the maximum documented ordinal, so ordinal `8794` is the last valid table index. Ordinals below `101` are possible array indexes but do not correspond to valid GB byte pairs under the documented scheme.

This header contains no include guards, but it only provides a macro and an `extern` declaration, so repeated inclusion would not define storage.

## Filesystem Relevance

This file is not filesystem code. It is OS userland conversion-tool infrastructure within the Plan 9 source tree.
