# sources/object-store/rustfs/crates/ecstore/src/store_test.rs

## Purpose

Unit-tests ECStore disk de-duplication so admin/storage inventory views do not overcount repeated `rustfs_madmin::Disk` records.

## Important APIs and Types

Uses `ECStore::deduplicate_disks` and `rustfs_madmin::Disk` fields such as endpoint, drive path, pool index, set index, disk index, and total space.

## Control Flow

One test creates 232 identical disks and expects one unique disk. Another creates two unique drive paths plus one duplicate and expects two disks.

## State and Persistence Behavior

No durable state. Tests construct in-memory DTOs and check a pure transformation.

## Dependencies and Integration Points

Depends on `ECStore` from `store.rs` and the admin disk DTO used by management APIs.

## Risks and Edge Cases

Tests do not cover partial identity differences, endpoint aliases, empty/default fields, or output ordering.

## Test Signals

Failures indicate duplicated disk reporting or possible capacity/inventory overcounting.
