# sources/user-network-fs/nfs-ganesha/src/support/rados_grace.c

## Purpose
This file manages NFSv4 grace-period cluster coordination state stored in a Ceph RADOS object. It tracks global current/recovery epochs and per-node flags indicating whether a node needs grace and whether it is enforcing grace locally.

## Important APIs, Types, And Functions
Public functions include `rados_grace_create`, `rados_grace_dump`, `rados_grace_epochs`, `rados_grace_enforcing_toggle`, `rados_grace_enforcing_check`, `rados_grace_join_bulk`, `rados_grace_lift_bulk`, `rados_grace_add`, and `rados_grace_member_bulk`. Internal `rados_grace_notify` sends a RADOS notification after successful state changes. Per-node omap values use flag bits `RADOS_GRACE_NEED_GRACE` and `RADOS_GRACE_ENFORCING`.

## Control Flow
The object body stores two little-endian `uint64_t` values: current epoch and recovery epoch. OMAP keys are node ids with one-byte flags. Create writes initial epochs. Dump and epochs read and decode the object. Join/lift/toggle/add functions use read-modify-write loops: read epochs and omap keys, capture object version with `rados_get_last_version`, compute updated flags/epochs, assert the version in a write op, then retry on version races. Lifting grace clears `NEED_GRACE` or removes node keys and sets recovery epoch to zero when all needing nodes are handled.

## State And Persistence
State is durable in RADOS: epochs in the object data and node flags in omap. In-memory arrays are temporary per call. Notifications are best-effort management signals after writes.

## Dependencies And Integration Points
The file depends on `librados`, endian helpers, errno values, and standard allocation. It integrates with NFSv4 recovery backends that need clustered grace coordination and node membership checks.

## Risks And Test Signals
Risks include hard `MAX_ITEMS` pagination limits producing `-ENOTRECOVERABLE` when exceeded, manual allocation cleanup paths, version-race retry behavior, node membership requiring all provided ids to exist, synchronous notify latency, and source anomalies such as duplicated `if (more)` text and suspicious brace structure in read loops that warrant compile/test confirmation. Tests should use a real or mocked RADOS cluster to cover create idempotency, add/member, join start/no-start, lift with remove and non-remove, enforcing toggle/check, concurrent writers causing version retries, more-than-1024 omap entries, malformed object body length, and notification failure tolerance.
