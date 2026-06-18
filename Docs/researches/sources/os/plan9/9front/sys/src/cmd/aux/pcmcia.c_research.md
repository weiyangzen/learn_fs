# File Research: sources/os/plan9/9front/sys/src/cmd/aux/pcmcia.c

`pcmcia` decodes PCMCIA CIS tuples from an attribute-memory file, defaulting to `#y/pcm0attr`. It reads every byte from even offsets (`2*pos`), reflecting attribute-memory layout, and prints parsed tuple information.

Supported tuple parsers include device descriptors, long-link multi-function tuples, version strings, configuration register location, configuration entries, function IDs, power descriptors, timing, I/O ranges, IRQ masks, and memory windows. `-x` also prints raw bytes as hex while reading.

The tuple dispatcher uses tuple type byte and link length, then advances to the next tuple by `next+2+link`. Long-link multi-function parsing recursively follows linked CIS chains.

Caveats: parsing is print-oriented and tolerant of partial reads; unhandled tuple types are skipped; tuple recursion and bad link targets can lead to confusing output but generally stop on read failure.
