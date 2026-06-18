# sources/test-tools/fio/lib/ffz.h

Purpose: implements "find first zero" bit helpers and a 64-bit find-first-set primitive used by bitmap code.

Important APIs/functions: `ffs64`, `ffz`, and `ffz64`. If `ARCH_HAVE_FFZ` is set, `ffz` maps to `arch_ffz`; otherwise it inverts the word and uses `ffs64`.

Control flow/state: pure inline bit scanning with staged masks for 32, 16, 8, 4, 2, and 1-bit narrowing. No state or allocation.

Dependencies/integration: includes integer types and optionally architecture-provided bit operations. `axmap.c` uses these helpers to find free positions.

Risks/test signals: return values for all-ones or zero inputs must match callers' expectations; `ffs64(0)` returns 64 after falling through, so callers should avoid undefined semantic cases or handle them explicitly. Tests should cover low/high bit positions and all-zero/all-one masks.
