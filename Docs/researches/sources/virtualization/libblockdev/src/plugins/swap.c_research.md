# File Research: sources/virtualization/libblockdev/src/plugins/swap.c

This file implements the swap plugin: creating swap signatures, activating/deactivating swap, querying active status, and setting/validating labels and UUIDs.

Dependency handling:
- Requires `mkswap >= 2.23.2` for creation.
- Requires `swaplabel` for label and UUID mutation.
- Caches dependency checks in `avail_deps`, protected by `deps_check_lock`.
- `bd_swap_close()` clears the dependency cache.
- `bd_swap_is_tech_avail()` maps requested tech modes to the required utility masks.

Core functions:
- `bd_swap_error_quark()` returns the swap error domain.
- `bd_swap_init()` is a no-op returning `TRUE`.
- `bd_swap_mkswap()` builds `mkswap -f`, optionally adds `-L <label>` and `-U <uuid>`, appends the target device, and passes extra args to `bd_utils_exec_and_report_error()`.
- `bd_swap_swapon()` validates the target with libblkid before calling the kernel `swapon()` syscall.
- `bd_swap_swapoff()` calls the kernel `swapoff()` syscall.
- `bd_swap_swapstatus()` scans `/proc/swaps` for the device path, resolving `/dev/mapper/` and `/dev/md/` paths first.
- `bd_swap_check_label()` enforces the 16-character swap label limit.
- `bd_swap_set_label()` runs `swaplabel -L <label> <device>`.
- `bd_swap_check_uuid()` checks ASCII and validates RFC-4122 parsing with `uuid_parse()`.
- `bd_swap_set_uuid()` runs `swaplabel -U <uuid> <device>`.

`bd_swap_swapon()` validation flow:
- Starts a progress task.
- Creates a blkid probe and opens the device read-only.
- Retries `blkid_probe_set_device()` and `blkid_do_safeprobe()` on transient busy states.
- Requires detected `TYPE=swap`.
- Rejects old `SWAP-SPACE`, suspend signatures `S1SUSPEND`/`S2SUSPEND`, and unknown signatures.
- Computes swap page size from `SBMAGIC_OFFSET + strlen(SBMAGIC)` and rejects mismatches with system page size.
- Applies optional priority with `SWAP_FLAG_PREFER` and priority bit packing.
- Calls `swapon()` and reports completion or a detailed error.

Research relevance:
- This plugin mixes direct syscalls with external util-linux commands.
- Activation is intentionally defensive to avoid enabling stale suspend images or incompatible swap formats.
- `bd_swap_swapstatus()` is path-prefix based against `/proc/swaps`, so exact path formatting and symlink resolution matter.
- UUID validation lowercases input before parsing to tolerate uppercase ASCII UUIDs.
