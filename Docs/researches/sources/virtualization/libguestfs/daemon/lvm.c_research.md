# File Research: sources/virtualization/libguestfs/daemon/lvm.c

Main LVM2 command wrapper.

Important behavior:
- Checks availability with `prog_exists("lvm")`.
- Lists PVs/VGs through `lvm pvs/vgs`, trims and sorts output, and suppresses `"unknown device"`.
- Creates/removes/resizes/renames PVs, VGs, and LVs using command-vector construction.
- Many mutating operations call `udev_settle`.
- `do_lvm_remove_all` is explicitly destructive and removes LVs, VGs, then PVs.
- UUID and membership APIs use `--unbuffered --noheadings -o <field>`.
- `lv_canonical` maps `/dev/mapper` or `/dev/dm-*` paths to canonical LV names by matching `st_rdev`.
- `do_vgmeta` writes `vgcfgbackup` to a temp file and returns it subject to protocol size limits.
- Includes PV/VG UUID regeneration helpers.

Filesystem relevance: central block-storage volume management layer for LVM-backed guest filesystems.
