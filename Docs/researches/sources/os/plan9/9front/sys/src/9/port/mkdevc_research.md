# File Research: sources/os/plan9/9front/sys/src/9/port/mkdevc

Kernel configuration generator that emits C tables and stubs from architecture config files.

Key responsibilities:
- Parses `dev`, `ip`, `link`, `misc`, and `port` sections.
- Emits `devtab[]`, link initialization, architecture tables, AD/SD interface tables, UART tables, VGA tables, IP protocol init tables, DTrace provider tables, and config metadata.
- Handles architecture-specific DMA stubs for x86-like targets.
- Emits fallback stubs when ramdisk, VGA screen, or DTrace support is absent.
- Preserves raw lines from the `port` section into generated C.

Important behavior:
- Rejects device counts >= 256 because `Pgrp.devmask` is one byte per 8 device IDs.
- Special-cases device names/prefixes: `ad`, `sd`, `uart`, `vga`, `dtracy`, and architecture entries.
- Generates `conffile` from current working directory and config argument, and `kerndate` from `KERNDATE`.

Dependencies:
- Uses Plan 9 `rc` and `awk`.
- Generated output depends on many headers such as `dat.h`, `fns.h`, `io.h`, `sd.h`, screen headers, and IP headers.

Notable risks:
- The parser is section/indentation-sensitive.
- Generated symbol names depend directly on config tokens.
