# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/tvp3026clock.c

TVP3026 pixel and loop clock parameter calculator.

Key behavior:
- Sets VGA misc clock-select bits for fixed VGA clocks or programmed clocks.
- Brute-force searches TVP3026 pixel PLL fields `m/n/p` for:
  - `Fvco = 8*RefFreq*(65-m)/(65-n)`
  - `Fpll = Fvco / 2**p`
- Enforces VCO range 110-250 MHz and nominal `n/m/p` constraints.
- Computes loop clock fields in `m/n/p/q[1]`, using enhanced-mode state to pick bus ratio.
- Marks `Finit`.

Integration:
- `s3clock.c` consumes these fields in `tvp3026load()`.

Filesystem relevance:
- Indirect display clock calculation.
