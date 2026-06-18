# File Research: sources/os/plan9/plan9/sys/src/9/boot/paq.c

Flash/paq boot method.

Key behavior:
- `configpaq()` binds flash/proc devices, opens `/dev/flash/flashctl`, and creates fixed flash partitions for bootloader, params, kernel, user, and ramdisk.
- `connectpaq()` forks `/boot/paqfs -v -i /dev/flash/ramdisk`, waits, and returns pipe fd.

This supports systems booting a paqfs image from flash ramdisk.
