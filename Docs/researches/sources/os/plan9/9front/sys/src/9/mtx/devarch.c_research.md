# File Research: sources/os/plan9/9front/sys/src/9/mtx/devarch.c

This file implements the MTX `#P/arch` device. It exposes raw I/O-port access files `iob`, `iow`, and `iol`, supports dynamic arch-file registration through `addarchfile`, initializes I/O allocation tracking, and provides PCMCIA special-hook wrappers.

`archread` and `archwrite` validate I/O port ranges through `checkport`, then perform byte/word/long reads and writes using `inb/ins/inl` and `outb/outs/outl`. Standard VGA ports are allowed; otherwise the port range must be allocated or unused as permitted by the I/O map.

Filesystem relevance is direct as a device file implementation. It adds namespace-visible files that privileged users or drivers can use for low-level hardware access.

Notable risks: raw port access is powerful and permission-sensitive; `archopen` uses the full fixed `archdir` array length rather than `narchdir` in `devopen`, though directory reads use dynamic count.
