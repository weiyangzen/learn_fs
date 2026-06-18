# File Research: sources/os/plan9/plan9/sys/src/9/kw/coproc.c

## Purpose
Provides dynamic ARM coprocessor and VFP register access helpers by generating short instruction sequences in memory, flushing caches, and calling them.

## Main Functions
- `cpwr`: emits an `MCR` instruction plus return, then executes it to write a coprocessor register.
- `cpwrsc`: CP15/system-control wrapper around `cpwr`.
- `cprd`: emits an `MRC` instruction plus return, then executes it to read a coprocessor register.
- `cprdsc`: CP15/system-control wrapper around `cprd`.
- `fprd`: emits `VMRS` to read a VFP register.
- `fpwr`: emits `VMSR` to write a VFP register.

## Dependencies and Integration
Uses interrupt masking, cache writeback/invalidate, instruction cache invalidation, caller-PC segment mapping, and constants from `arm.h`.

## Risks and Notes
This approach depends on executable stack/data mapping behavior via `MAP2PCSPACE`, careful cache synchronization, and correct instruction encoding. It is powerful but architecture-specific.
