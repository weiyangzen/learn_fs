# File Research: sources/virtualization/libguestfs/daemon/modprobe.c

Kernel module loading wrapper.

Important behavior:
- Optgroup availability returns false when `/proc/modules` is absent with `ENOENT`.
- Otherwise requires `modprobe` to exist.
- `do_modprobe(module)` runs `modprobe <module>` and returns the process status.

Filesystem relevance: enables loading kernel modules needed for filesystem, block, or device support in the appliance.
