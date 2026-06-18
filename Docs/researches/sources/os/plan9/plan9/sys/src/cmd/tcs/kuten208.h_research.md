# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.h

## Purpose

`kuten208.h` declares the JIS X 0208 mapping table contract.

## Contents

- `#define KUTEN208MAX 8407`
- `extern long tabkuten208[KUTEN208MAX];`

## Integration

`conv_jis.c` uses `KUTEN208MAX` for bounds checks before indexing `tabkuten208`. `font/kmap.c` also iterates exactly `KUTEN208MAX` entries. The macro must match the initializer length in `kuten208.c`.
