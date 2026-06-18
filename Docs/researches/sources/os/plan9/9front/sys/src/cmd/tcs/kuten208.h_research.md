# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/kuten208.h

## Purpose
Defines the fixed size and extern declaration for the JIS X 0208 kuten mapping table.

## Key Elements
Defines `KUTEN208MAX` as `8407` and declares `extern long tabkuten208[KUTEN208MAX];`.

## Dependencies
Included by `kuten208.c`, `conv_jis.c`, and `font/kmap.c`.

## Behavior/Risks
No include guard is present. The fixed maximum must remain synchronized with the initializer in `kuten208.c`; `conv_jis.c` uses it for bounds checks and reverse lookup construction.

## Verification
Read completely: 3 lines, 94 bytes. SHA-256: `952d40bfdf81091f24103eda3742ad5167a307e9a5588187e379bfb6c26788ce`.
