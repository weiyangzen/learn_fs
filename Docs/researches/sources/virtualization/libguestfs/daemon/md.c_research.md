# File Research: sources/virtualization/libguestfs/daemon/md.c

Wraps mdadm RAID operations and mdstat parsing.

Important behavior:
- Optgroup availability checks `mdadm`.
- OCaml noalloc helper tests whether a device is a real RAID array via `GET_ARRAY_INFO` when available.
- `do_md_create` validates optional level, chunk alignment, spare count, nrdevices, and missingbitmap invariants.
- Builds `mdadm --create --run` with real devices and `"missing"` placeholders.
- `do_md_stop` runs `mdadm --stop`.
- `do_md_stat` parses `/proc/mdstat` for a named array and returns device/index/flag entries.

Filesystem relevance: manages Linux software RAID devices that can contain filesystems or higher storage layers.
