# File Research: sources/os/plan9/9front/sys/src/9/mtx/dat.h

This is the MTX platform data-structure header. It defines forward declarations, syscall argument count, executable magic, machine-dependent `Label`, `FPsave`, `PFPU`, FP state enum, `Confmem`, `Conf`, per-process `PMMU`, fake `KMap` macros, `Mach`, active-machine state, and `ISAConf`.

`FPsave` must match assembly `fpsave`/`fprestore`. `Mach` has fields known to assembly at the front: `machno`, `splpc`, and current `Proc*`; later fields include page-table base, MMU PID/color state, CPU timing, and kernel stack.

Filesystem relevance is structural: `Conf` sizes process/page/image/swap resources, `PMMU` drives per-process address-space IDs, and fake kmap determines how physical pages are addressed by kernel code.

Notable risks: fake kmap assumes direct mapping via `KZERO`; `Mach` layout is coupled to `l.s`; `NCOLOR` is fixed to 1, simplifying cache-color behavior.
