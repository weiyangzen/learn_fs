# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/big5.c

Defines the Big5-to-Unicode mapping table for `tcs`.

Key points:
- Includes `big5.h` and defines `long tabbig5[BIG5MAX]`.
- The table has `BIG5MAX` entries, 13,973 total.
- Entries are Unicode code points for Big5 ordinals; unmapped entries are `-1`.
- Reading/counting found 270 invalid `-1` slots.
- Non-invalid values range from `0x23` through `0xff5d`; the first entry is `0x3000`.
- The table covers punctuation, fullwidth forms, symbols, radicals, CJK ideographs, and extended Big5 ranges, ending with unmapped padding slots.

Dependencies and interactions:
- Size and extern declaration come from `big5.h`.
- Consumed by the `tcs` charset conversion implementation when decoding Big5 input.

Research relevance:
- Large static charset data table, not executable logic, but essential for Big5 conversion.
