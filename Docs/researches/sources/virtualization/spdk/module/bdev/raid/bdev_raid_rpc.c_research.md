# File Research: sources/virtualization/spdk/module/bdev/raid/bdev_raid_rpc.c

This file implements JSON-RPC methods for managing RAID bdevs.

`bdev_raid_get_bdevs` decodes a required `category` state selector, iterates `g_raid_bdev_list`, and emits RAID objects whose state matches the requested category or `all`. Each object includes name, UUID, and the shared `raid_bdev_write_info_json()` output, which includes strip size, state, level, superblock flag, base counts, process progress, and base slot details.

`bdev_raid_create` decodes `name`, optional `strip_size_kb`, `raid_level`, `base_bdevs`, optional `uuid`, and optional `superblock`. It rejects empty base names, then calls `raid_bdev_create()`. Creation is asynchronous; `rpc_bdev_raid_create_cb()` returns boolean true or a formatted error and frees the heap-decoded autogen context.

`bdev_raid_delete` decodes `name` and optional `clear_sb`, resolves the RAID object by name, then calls `raid_bdev_delete()`. Completion is asynchronous through `bdev_raid_delete_done()`, which logs failures and returns JSON boolean true on success.

`bdev_raid_add_base_bdev` decodes a base bdev name and RAID bdev name, resolves the RAID object, and calls `raid_bdev_add_base_bdev()`. This is the RPC entry point for replacing/re-adding members, potentially triggering rebuild in the core. `bdev_raid_remove_base_bdev` decodes a base bdev name, opens it read-only long enough to get the `spdk_bdev *`, calls `raid_bdev_remove_base_bdev()`, closes the descriptor, and reports async completion through `rpc_bdev_raid_remove_base_bdev_done()`.

`bdev_raid_set_options` decodes optional background process tunables. It first loads current options, overlays any provided fields, calls `raid_bdev_set_opts()`, and returns a boolean. It is registered for both startup and runtime.

The file mostly delegates validation to the RAID core and autogen decoders. Error conventions use negative errno-style RPC codes for many domain errors and JSON-RPC parse/internal codes for decode failures depending on handler.
