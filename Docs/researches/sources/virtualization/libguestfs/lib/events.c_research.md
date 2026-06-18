# File Research: sources/virtualization/libguestfs/lib/events.c

Purpose: Implements the modern event callback registry plus compatibility wrappers for older single-callback APIs.

Key behavior:
- `guestfs_set_event_callback` appends callbacks to `g->events`, returning an integer event handle; flags must be zero and callback count is capped at 1000.
- `guestfs_delete_event_callback` disables callbacks by zeroing their bitmask and shrinks the tail entry when possible.
- Internal dispatchers call matching callbacks for void, message, and uint64-array payloads.
- If no message callback is registered, appliance/library/warning/trace messages are printed to stderr with escaping rules for binary and control characters.
- Old APIs such as `guestfs_set_log_message_callback`, `guestfs_set_close_callback`, and `guestfs_set_progress_callback` are emulated with wrapper callbacks stored in `opaque2`.

Dependencies and state:
- Uses `g->events` and `g->nr_events` from `guestfs_h`.
- Uses `c_isprint`, `STREQ/STRNEQ`, and handle locking on public registration/removal APIs.

Risks:
- Registry is a linear array with a hard limit; deleted non-tail entries remain as inert slots.
- Old-style callback replacement uses wrapper function identity as the sentinel, so one callback per old event type is preserved by design.
