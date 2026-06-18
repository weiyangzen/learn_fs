# File Research: sources/os/plan9/9front/sys/src/cmd/acme/fns.h

This header declares cross-module Acme functions and helper macros.

Key contents:
- Warning/error, plumbing, snarf, temp-file, scroll, font, argument, command, file, search, edit, execution, fsys, regex, allocation, address, and conversion prototypes.
- `fbufalloc()`/`fbuffree()` macros for fixed-size rune/byte work buffers.
- Rune allocation macros wrapping `emalloc`/`erealloc`.
- 9P server prototypes including `fsysinit()`, `fsysmount()`, `respond()`, xfid handlers, and log handlers.
- Address and regex helpers used by both UI and file server paths.

Filesystem/storage relevance:
- Declares the public surface for Acme's synthetic filesystem, text loading, file putting, and buffer-backed editing.

Notes:
- This file is the coupling point among otherwise separate Acme translation units.
