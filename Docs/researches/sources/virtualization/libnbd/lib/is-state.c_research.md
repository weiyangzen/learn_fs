# File Research: sources/virtualization/libnbd/lib/is-state.c

Defines internal and public state classification helpers.

Key functions:
- Internal predicates for created, connecting, negotiating, ready, processing, dead, and closed.
- Connecting and processing use generated state-group hierarchy rather than enumerating every concrete state.
- Public `nbd_unlocked_aio_is_*` APIs read `public_state`.
- `nbd_unlocked_aio_get_direction` returns public-state poll direction.

Interactions:
- Depends on generated `nbd_internal_state_group`, `nbd_internal_state_group_parent`, and `nbd_internal_aio_get_direction`.
- Other internal code should use internal predicates on `state`, not public API predicates.

Research notes:
- The file documents the distinction between real internal state and externally visible state.
