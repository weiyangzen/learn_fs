# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_rndblock/npfext_rndblock.c

## Summary
Implements userland parameter parsing for the NPF `rndblock` extension.

## Main Responsibilities
- Construct extension objects named `rndblock`.
- Require values for all parameters.
- Parse `mod` as an integer in `[1, LONG_MAX]`.
- Parse `percentage` as floating-point percent multiplied by 100 for kernel units based on 10000.
- Enforce `percentage` range `[1, 9999]`.
- Store values as u32 extension parameters.

## Risks
Parsing uses `atol()`/`atof()`, so malformed text may be accepted as zero and then rejected by range checks. Floating-point truncation determines final percentage precision.
