# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun2.c

Sun2 libkvm MMU support for m68k crash dumps. It registers `_kvm_ops_sun2`, points `vmst->private` at the dump-embedded PMEG table, and translates kernel virtual addresses through the Sun2 segment map and PMEG PTE array.

Live-kernel `vatop` is rejected. Physical addresses map directly to `dump_off + pa`.
