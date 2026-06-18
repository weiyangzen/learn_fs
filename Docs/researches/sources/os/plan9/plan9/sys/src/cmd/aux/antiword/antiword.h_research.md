# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/antiword.h

This is Antiword’s central project header. It defines platform constants, common macros, path names, output defaults, and prototypes for nearly every Antiword module.

Key behavior:
- Enforces exactly one of `DEBUG` or `NDEBUG`.
- Provides fallback definitions for `PATH_MAX`, time and size limits, separators, screen widths, margins, font names, mapping files, and platform-specific Antiword directories.
- Defines common comparison, rounding, bit, min/max, and element-count macros.
- Declares public functions across document detection, OLE/block depot handling, text/data block lists, character conversion, rendering backends, image translation, property parsing, fonts, lists, notes, options, output, and memory helpers.

Important details:
- The Plan 9 configuration uses `GLOBAL_ANTIWORD_DIR` as `/sys/lib/antiword`, local `ANTIWORD_DIR` as `lib/antiword`, and `fontnames` as the font-name file.
- RISC OS-specific GUI/drawfile APIs are conditionally exposed.
- The header is the coupling point between parsing, formatting, image, and output subsystems.

Filesystem relevance:
- Indirect to direct configuration relevance: defines where Antiword searches runtime support files such as character maps and font-name tables.
