# File Research: sources/virtualization/spdk/lib/ublk/ublk_rpc.c

This file exposes JSON-RPC methods for the ublk target and ublk-backed disks.

`ublk_create_target` decodes optional `cpumask` and `disable_user_copy`, calls `ublk_create_target()`, and returns a boolean. `ublk_destroy_target` calls the async destroy helper and sends the response from `ublk_destroy_target_done()` after teardown completes.

`ublk_start_disk` decodes `bdev_name`, `ublk_id`, and optional `num_queues`/`queue_depth` with defaults from `ublk_internal.h`. It heap-allocates request context because disk creation is asynchronous, then returns the ublk ID on completion or a JSON-RPC error on failure.

`ublk_stop_disk` decodes `ublk_id`, calls `ublk_stop_disk()`, and returns from an async completion callback. As read, its completion callback always sends boolean success and ignores the callback `rc`, while immediate start errors are returned as JSON-RPC errors.

`ublk_get_disks` optionally filters by `ublk_id`; otherwise it iterates all ublk devices. Each object reports `/dev/ublkb<ID>`, numeric ID, queue depth, queue count, and backing bdev name.

`ublk_recover_disk` decodes `bdev_name` and `ublk_id` and calls `ublk_start_disk_recovery()`. Unlike normal disk start, it passes no control callback and immediately sends a response based on command submission return code, not final recovery completion.

The file relies on generated RPC context free helpers from `spdk_internal/rpc_autogen.h` and the internal ublk API. All RPCs are runtime-registered.
