# File Research: sources/virtualization/virtiofsd/src/soft_idmap/mod.rs

## Purpose

This file implements runtime soft UID/GID mapping between guest and host ID domains. It converts parsed command-line mapping rules into efficient non-overlapping range maps and provides lookup functions in both directions.

## Module Structure

- `pub mod cmdline`: command-line syntax and parsing.
- `pub mod id_types`: strong host/guest UID/GID types.
- Re-exports: `GuestGid`, `GuestId`, `GuestUid`, `HostGid`, `HostId`, `HostUid`, `Id`.

## Main Types

- `IdMap<Guest, Host>`: bidirectional mapping container for one ID family, either UID or GID.
  - `guest_to_host: RangeMap<Guest::Inner, MapEntry<Guest, Host>>`
  - `host_to_guest: RangeMap<Host::Inner, MapEntry<Host, Guest>>`

- `MapEntry<Source, Target>`:
  - `Squash { from, to }`: maps a source range to one target ID.
  - `Range { from, to_base }`: maps a source range 1:1 to a target range.
  - `Fail { from }`: explicitly rejects source IDs.

- `MapError<Source>`:
  - `ExplicitFailMapping { id }`

## Mapping Behavior

`IdMap::empty()` creates maps with no explicit entries. Unmapped IDs are identity-mapped numerically through `id_mapped()`.

`map_guest(guest_id)` looks up the guest raw value in `guest_to_host`; if found, the matching `MapEntry` maps or fails the ID. If not found, it returns identity-mapped host ID.

`map_host(host_id)` does the same in the host-to-guest direction.

`MapEntry::map()`:

- `Squash`: returns the single configured target ID.
- `Range`: returns `to_base + (id - from.start)`.
- `Fail`: returns `MapError::ExplicitFailMapping`.

Each branch asserts that the ID is inside the source range.

## Construction And Validation

`do_push()` inserts a `MapEntry` into a `RangeMap`. It converts the typed source range to the raw inner range and rejects any entry that intersects an existing entry. On overlap, it returns an `io::Error` describing the map direction and conflicting entry.

`id_range_from_u32(base, count, param)` constructs a typed half-open range from `base..base+count`, returning `InvalidInput` if `base + count` overflows `u32`.

`TryFrom<Vec<cmdline::IdMap>> for IdMap<Guest, Host>` converts each command-line rule:

- `Guest`: adds guest-to-host `Range`.
- `Host`: adds host-to-guest `Range`.
- `SquashGuest`: adds guest-to-host `Squash`.
- `SquashHost`: adds host-to-guest `Squash`.
- `Bidirectional`: adds both directions as `Range`.
- `ForbidGuest`: adds guest-to-host `Fail`.

Errors are decorated with the original command-line entry using `ResultErrorContext`.

## Integration Points

This module consumes `cmdline::IdMap` and typed IDs from `id_types.rs`. It uses `btree_range_map::RangeMap` for intersection detection and lookup. Mapping errors convert to `io::ErrorKind::PermissionDenied`, allowing filesystem operations to fail naturally when a forbidden guest ID is used.

The module is used by virtiofsd soft ID mapping paths elsewhere in the crate, and `GuestGid` is used directly by FUSE extension parsing in `server.rs`.

## Important Invariants

- Explicit mappings in the same direction must not overlap.
- Guest-to-host and host-to-guest maps are independent; they do not need to be inverses.
- Empty maps are identity maps, not deny-all maps.
- Range ends are half-open.
- Runtime range construction checks overflow for most variants through `id_range_from_u32`.

## Risks And Edge Cases

- `ForbidGuest` constructs `(from_guest.into())..((from_guest + count).into())` directly and does not use `checked_add`; this can overflow in debug builds or wrap in release depending on compilation settings.
- `MapEntry::map()` uses assertions for containment, relying on `RangeMap` correctness.
- Arithmetic in ID wrappers can overflow or underflow if bad ranges slip through.
- Bidirectional mapping can fail halfway if the reverse direction overlaps after the forward entry was inserted, leaving the local construction object partially modified before returning an error. Since construction returns `Err`, callers should discard it.
