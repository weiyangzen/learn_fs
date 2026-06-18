# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/heartbeat.h

## Summary
Declares the O2CB heartbeat API, callback types, callback registration structure, and heartbeat timing constants.

## Main Responsibilities
- Define region timeout, live/dead thresholds, max region name length, and callback magic.
- Define node up/down callback event types.
- Define `struct o2hb_callback_func`.
- Expose heartbeat configfs group allocation, lifecycle, callback, liveness, and region utility APIs.

## Key Interfaces
- `o2hb_register_callback()` and `o2hb_unregister_callback()` connect cluster subsystems to node events.
- `o2hb_fill_node_map()` gives a serialized live-node bitmap.
- `o2hb_stop_all_regions()` is used before fencing or emergency shutdown paths.
- `o2hb_global_heartbeat_active()` reports the configured heartbeat mode.

## Risks
Callback users must initialize with `o2hb_setup_callback()` and respect callback-context locking expectations, especially when using `_from_callback()` helpers.
