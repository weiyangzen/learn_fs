# File Research: sources/virtualization/libnbd/lib/flags.c

Maintains negotiated export size, export flags, block constraints, payload limit, and public feature queries.

Key functions:
- `nbd_internal_reset_size_and_flags`: clears export size, flags, block sizes, payload cap, canonical name, and description.
- `nbd_internal_set_size_and_flags`: validates nonzero eflags, masks inconsistent server claims, handles metadata-valid shortcut, then records export size/flags.
- `nbd_internal_set_block_size`: validates server-advertised block size constraints and ignores malformed advertisements.
- `nbd_internal_set_payload`: derives max payload from block maximum or defaults to 32 MiB.
- `nbd_unlocked_can_*` and `is_*`: query per-export feature flags.
- `nbd_unlocked_can_meta_context`: checks negotiated metadata context names.
- `nbd_unlocked_get_size`: returns export size with signed overflow guard.
- `nbd_unlocked_get_block_size`: returns minimum/preferred/maximum/payload sizes.

Interactions:
- State machine calls internal setters during negotiation.
- `rw.c` uses feature queries to enforce strict command validation.

Research notes:
- The file tolerates some invalid server feature combinations by clearing dependent flags instead of failing.
- Export size is considered valid only after `eflags != 0`.
