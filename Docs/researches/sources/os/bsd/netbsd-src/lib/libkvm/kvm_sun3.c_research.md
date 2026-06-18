# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3.c

Sun3 variant of the Sun m68k libkvm translator. It uses 256 kernel segment entries, reads PMEG entries from the crash dump CPU data, checks PTE validity, and returns the translated physical page plus page offset.

The physical-to-dump mapping is direct: `kd->dump_off + pa`.
