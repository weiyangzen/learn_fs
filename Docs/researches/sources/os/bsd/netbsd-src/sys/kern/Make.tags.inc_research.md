# File Research: sources/os/bsd/netbsd-src/sys/kern/Make.tags.inc

## Purpose
Provides common make logic for generating kernel source tags across architecture builds.

## Main Interfaces
- Under `.ifmake tags`, defines `SYSDIR`, `FINDCOMM`, and `COMM`.
- `FINDCOMM` finds common `*.[ch]` files while pruning architecture and selected generated/vendor/problematic directories/files.

## Implementation Notes
The comment explains common files are placed near the end so function tags win over struct tags with the same name.

## Dependencies
Included by architecture-specific kernel tag makefiles and relies on BSD make conditionals and shell `find`/`sort`.
