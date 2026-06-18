# File Research: sources/virtualization/qemu/block/throttle.c

`throttle.c` implements the QEMU block filter driver named `"throttle"`. It attaches a block node to an existing throttle group and intercepts I/O requests to enforce the group's shared limits.

The only driver-specific open option is `throttle-group`. `throttle_parse_options()` absorbs options through `throttle_opts`, requires a group name, and verifies that the named group already exists with `throttle_group_exists()`. On success it returns a duplicated group name. `throttle_open()` opens the `"file"` child, inherits supported write/zero flags from the child while adding `BDRV_REQ_WRITE_UNCHANGED`, parses the group, and registers the node's `ThrottleGroupMember` with `throttle_group_register_tgm()` using the block node's AIO context.

The filter forwards data operations after interception. `throttle_co_preadv()` calls `throttle_group_co_io_limits_intercept(tgm, bytes, THROTTLE_READ)` before forwarding to `bdrv_co_preadv()`. `throttle_co_pwritev()`, `throttle_co_pwrite_zeroes()`, and `throttle_co_pdiscard()` intercept as `THROTTLE_WRITE` before forwarding. Compressed writes reuse `throttle_co_pwritev()` with `BDRV_REQ_WRITE_COMPRESSED`. Flush and getlength forward directly to the child.

AIO context hooks delegate to the group layer: `throttle_detach_aio_context()` detaches timers, and `throttle_attach_aio_context()` reattaches them in the new context. Reopen support reparses the target group in prepare, then on commit unregisters/reregisters the member if the group name changed; abort frees the prepared group string.

Drain handling disables limits while draining. `throttle_drain_begin()` atomically increments `io_limits_disabled` and restarts the member if this is the first disable. `throttle_drain_end()` decrements and asserts the disable count was nonzero. This prevents drain from waiting behind throttled requests.

`bdrv_throttle` is marked `is_filter = true`, uses default child permissions, has `instance_size = sizeof(ThrottleGroupMember)`, and declares `throttle-group` as a strong runtime option. Close unregisters the member from its group.
