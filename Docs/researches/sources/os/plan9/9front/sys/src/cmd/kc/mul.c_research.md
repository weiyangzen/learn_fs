# File Research: sources/os/plan9/9front/sys/src/cmd/kc/mul.c

Constant-multiply sequence generator for the compiler. It searches for short shift/add/sub instruction strings that multiply by a constant, caches recent constants in `multab`, and falls back to a large curated hint table for constants the search misses. The mini-language encodes shifts as letters and arithmetic as `+`/`-` plus operand selection digits.

`mulcon0` normalizes negative constants, checks cache, probes hints, searches up to bounded sequence length, and recursively handles trailing powers of two. `docode`, `gen1`, `gen2`, and `gen3` perform the constrained search and validate candidate sequences against `mulval`. The result is consumed by `swt.c:mulcon` to emit real SPARC operations.
