# File Research: sources/os/plan9/9front/sys/src/9/bcm64/gisb.c

BCM GISB arbiter bus-error reporting support.

Key responsibilities:
- Maps GISB arbiter registers at `VIRTIO2+0x400000`.
- Reads captured bus-error status, address, data, master, and interrupt state.
- Clears captured errors and interrupt bits.
- Prints detailed timeout/abort read/write diagnostics.
- Installs `arberror()` as the trap bus-error hook and periodically polls via clock callback.

Dependencies:
- Trap bus-error hook, clock callback registration, BCM GISB registers, and kernel diagnostic output.
