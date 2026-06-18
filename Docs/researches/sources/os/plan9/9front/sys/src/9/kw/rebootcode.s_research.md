# File Research: sources/os/plan9/9front/sys/src/9/kw/rebootcode.s

Kirkwood reboot trampoline assembly copied to `REBOOTADDR` before reboot. It disables caches/MMU safely, remaps low physical memory, copies the already-loaded new kernel image to its physical destination, flushes caches, and jumps to the new kernel entry.

`main` receives physical entry, source, and byte count. `cachesoff` flushes caches, disables cache bits, recreates identity mappings, invalidates TLBs, and reverts addressing state so the MMU can be disabled. Local implementations of `_r15warp`, `mmudisable`, `mmuinvalidate`, and `cacheuwbinv` make the trampoline self-contained.

Notable risks: code must run safely while transitioning away from the normal kernel mapping; it avoids loader-reserved registers and uses a tiny stack near the destination.
