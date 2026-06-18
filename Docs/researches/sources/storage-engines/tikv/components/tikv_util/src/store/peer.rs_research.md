# sources/storage-engines/tikv/components/tikv_util/src/store/peer.rs

## Purpose
Provides small helper functions for locating, mutating, removing, and constructing `kvproto::metapb::Peer` values inside a region.

## Important APIs, Types, and Functions
- `find_peer`, `find_peer_mut`, and `find_peer_by_id` search region peer lists.
- `remove_peer` removes the first peer with a matching store ID.
- Constructors include `new_peer`, `new_incoming_voter`, `new_learner_peer`, and `new_witness_peer`.
- `is_learner` checks `PeerRole::Learner`.

## Control Flow
Search helpers iterate the region peer vector. Constructors initialize default peers, set store ID, peer ID, role, and witness flag when needed. `remove_peer` finds a position then removes from `mut_peers`.

## State and Persistence Behavior
Functions mutate only the supplied `Region` or returned `Peer`; there is no global state.

## Dependencies and Integration Points
Depends on `kvproto::metapb::{Peer,PeerRole,Region}`. These helpers are re-exported by `store/mod.rs` and used in tests and region-manipulation code.

## Risks
`remove_peer` matches by store ID rather than peer ID, which is correct for many region operations but can surprise callers expecting peer-ID removal. Constructors do not set extra metadata beyond role/witness fields.

## Test Signals
The unit test checks voter/learner construction, learner detection, successful removal, idempotent missing removal, and post-removal lookup failure.
