# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regex2.h

Internal regex representation header. It defines magic values, strip operator encoding, all regex opcodes, character-set representation, `CHIN()` membership helpers, and `struct re_guts`.

Key concepts:
- A compiled regex is a strip of `sop` operators with opcode and operand packed into 32 bits.
- Operators include characters, anchors, any, character sets, backrefs, repetition delimiters, parentheses, alternation, BOS/EOS, and word boundaries.
- `cset` stores bitmap entries for small chars plus wide chars, ranges, character classes, inversion, and case-insensitive behavior.
- `struct re_guts` stores the strip, csets, flags, state counts, optimization literal (`must`), Boyer-Moore jump tables, subexpression count, backreference marker, and plus nesting depth.

This header is consumed by both compiler and executor and is not public ABI.
