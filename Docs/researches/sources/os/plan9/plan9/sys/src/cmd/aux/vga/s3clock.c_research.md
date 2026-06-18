# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3clock.c

S3-specific clock loading shim for external or RAMDAC-resident clock generators.

Key behavior:
- Knows how to load:
  - `icd2061a`
  - `ch9294`
  - `tvp3025clock`
  - `tvp3026clock`
- For ICD2061A, serializes a 24-bit programming word through S3 `Crt42` using the required unlock and modified Manchester sequence.
- For CH9294, selects the S3 clock index through `Crt42`.
- For TVP3025/3026, writes RAMDAC PLL registers and associated S3 clock-select state.
- Calls the selected clock controller’s `init()` if needed and sets VGA misc clock-select bits for non-standard clocks.

Important details:
- ICD2061A load is repeated three times, matching old hardware programming folklore.
- TVP3026 load includes busy-wait loops for PLL lock bits.

Filesystem relevance:
- Indirect hardware clock programming.
