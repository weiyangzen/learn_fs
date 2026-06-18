# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.h

## Purpose

`gbk.h` provides the public constants and table declaration needed by the GBK converter implementation.

## Contents

- `#define GBKMIN 0x8140`
- `#define GBKMAX 0xFE50`
- `extern long tabgbk[];`

Full-file validation:
- Lines: 4
- Bytes: 67
- SHA-256: `ff5c23981d84f1ff743d4b8831078b9c1855a930353f18a22e8fd3f3582ec523`

## Integration Points

- Included by `gbk.c` to define/export the mapping table with the shared constants.
- Included by `conv_gbk.c` to decode GBK input and build GBK output mappings.

## Important Notes

`GBKMAX` is used by the converter as an exclusive bound (`c < GBKMAX`, `i < GBKMAX`), so the valid encoded GBK range is `0x8140` through `0xfe4f`, not including `0xfe50`.
