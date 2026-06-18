# File Research: sources/virtualization/guestfs-tools/format/format.c

Implementation of `virt-format`, a destructive tool that erases and optionally repartitions/formats guest disk images.

Major behavior:
- Uses writable libguestfs handle.
- Accepts only `-a` disk inputs, not domains.
- Enables discard `besteffort` for added drives.
- Options include `--filesystem`, `--label`, `--lvm`, `--partition`, `--wipe`, `--format`, and `--blocksize`.
- Warns in usage text that all disk data is erased.

Formatting process:
1. Adds drives and launches libguestfs.
2. Checks whether `wipefs` API is available.
3. Erases filesystem signatures and partition tables with `wipefs` plus `zero`, or wipes whole devices with `zero_device` when `--wipe` is used.
4. Attempts `blkdiscard` for host space reclamation but ignores failures.
5. Rescans partition tables and LVM metadata.
6. Retries once with a fresh libguestfs handle if rescan fails.
7. Optionally partitions each disk:
   - Default chooses MBR under 2 TiB, GPT otherwise.
   - For MBR, sets partition type byte based on LVM or filesystem.
8. Optionally creates PV/VG/LV from `--lvm`.
9. Optionally creates filesystem via `guestfs_mkfs_opts_argv`, with label support.
10. Syncs and shuts down.

Notable helper:
- `parse_vg_lv` accepts `/dev/VG/LV` or `VG/LV`, rejects malformed names.

Research relevance: demonstrates libguestfs block-device destructive operations, partition-table recreation, LVM provisioning, filesystem creation, discard, and retry handling for kernel rescan instability.
