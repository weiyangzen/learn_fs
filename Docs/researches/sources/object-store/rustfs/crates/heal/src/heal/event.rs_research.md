<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/event.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/event.rs

## Purpose

`event.rs` defines heal-domain events and converts them into `HealRequest` values. It also provides a small bounded in-memory event handler for storing, filtering, and clearing recent events. This file is a classification and request-construction layer rather than an async scheduler.

## Important APIs, types, and functions

- `CorruptionType` classifies data, metadata, partial, and complete corruption.
- `Severity` is ordered from `Low` through `Critical` and maps to heal priority.
- `HealEvent` variants cover object corruption, missing object, metadata corruption, disk status changes, EC decode failure, checksum mismatch, bucket metadata corruption, and MRF metadata corruption.
- `HealEvent::to_heal_request` maps events into `HealType::{Object, Metadata, ErasureSet, ECDecode, Bucket, MRF}` with default options and severity-derived or fixed priority.
- `severity_to_priority` maps low/medium/high/critical to low/normal/high/urgent.
- `description` builds human-readable event strings.
- `severity` returns effective severity for each event kind.
- `timestamp` returns `SystemTime::now()` when called.
- `HealEventHandler` stores up to `max_events` events in a `Vec`, evicting the oldest when full.
- Handler methods include `add_event`, `get_events`, `clear_events`, `event_count`, `filter_by_severity`, and `filter_by_type`.

## Control flow

`to_heal_request` pattern matches the event. Object-corruption requests preserve version id and derive priority from explicit severity. Object-missing, checksum, bucket metadata, MRF metadata, and metadata-corruption events use high priority. EC decode failures use urgent priority. Disk status changes derive a set disk id from the endpoint pool/set indexes and create an erasure-set request with an empty bucket list; invalid endpoint indexes return `InvalidHealType`.

The event handler is synchronous. Adding to a full handler removes `events[0]`, then pushes the new event. Filtering by severity uses the enum's ordering. Filtering by type matches fixed string names.

## State and persistence behavior

There is no durable persistence. `HealEventHandler` is an in-memory bounded vector with O(n) oldest removal and O(n) filters. `timestamp` does not read a stored event timestamp; it returns the current time on each call, so event time is not preserved in `HealEvent`.

## Dependencies and integration points

This file uses internal `HealOptions`, `HealPriority`, `HealRequest`, and `HealType`, the crate `Error`/`Result`, and `rustfs_ecstore::disk::endpoint::Endpoint` for disk events. Disk event conversion uses `crate::heal::utils::format_set_disk_id_from_i32`, so it must stay consistent with manager/channel erasure-set key normalization.

## Risks and edge cases

- Disk-status events produce erasure-set requests with empty bucket vectors. Callers must populate bucket lists or storage execution will have nothing to scan.
- Event timestamps are not intrinsic to events, so callers cannot reconstruct detection time from an event instance.
- `filter_by_type` depends on exact string literals and has no enum-safe selector API.
- `add_event` removes from the front of a `Vec`, which is acceptable for the default 1000 events but is O(n).
- Event details such as missing/available shard/location vectors influence descriptions but not request options.

## Test signals

Tests cover event-to-request mapping for object, missing object, metadata, EC decode, checksum, bucket metadata, and MRF events; severity-to-priority mapping; descriptions; severity calculation; handler construction/defaults; bounded eviction; clear/get; and filtering by severity/type. Additional coverage should include disk-status conversion success/failure and the empty-bucket handoff requirement.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/event.rs -->
