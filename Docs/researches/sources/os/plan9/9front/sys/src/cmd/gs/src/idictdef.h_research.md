# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idictdef.h

Defines dictionary implementation internals and packed-key search macros.

Key points:
- Documents dictionary structure: keys, values, count, maxlength, and memory refs.
- Explains distinction between client capacity `C` and allocated slots `M`, including power-of-two rounding.
- Defines packed and unpacked key marker conventions for empty and deleted entries.
- Notes the first entry is always deleted to reduce wraparound cost.
- Defines helpers for packed-state checks, packed key sentinels, packed name keys, length/capacity/slot counts.
- Provides split packed-search macros used by both dictionary and dictionary-stack lookup code.

Research notes:
- This is included by implementation and high-performance clients.
- The macros intentionally expose free variables, so callers must set up names exactly as expected.
