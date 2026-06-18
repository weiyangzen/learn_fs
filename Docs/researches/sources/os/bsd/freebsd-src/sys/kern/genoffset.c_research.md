# File Research: sources/os/bsd/freebsd-src/sys/kern/genoffset.c

## Summary
Small C source used to emit structure field offset symbols for kernel assembly/header generation.

## Main Contents
Defines `GENOFFSET` unless `OFFSET_TEST` is set, includes kernel headers, and invokes `OFFSYM()` for selected `struct thread` fields: `td_priority`, `td_critnest`, `td_pinned`, and `td_owepreempt`.

## Integration
The object produced from this file is consumed by `genoffset.sh`, which reads `__assym_offset__` symbols and generates a lightweight C structure/offset assertion header.

## Risks
This file must stay synchronized with low-level code that needs thread-field offsets. Wrong field type declarations in `OFFSYM()` would make generated offset validation misleading.
