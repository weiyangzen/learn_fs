# sources/storage-engines/foundationdb/fdbclient/TagThrottle.cpp

## Purpose
`TagThrottle.cpp` implements transaction tag set handling and the persistent key encoding for tag throttles. It supports client validation limits, readable tag messages, key serialization for throttle records, and value decoding.

## Important APIs, types, and functions
`ClientTagThrottleLimits::NO_EXPIRATION` is the sentinel expiration time. `TagSet::addTag()` validates and deduplicates transaction tags. `TagSet::size()` and `TagSet::toString()` expose tag count and user-facing descriptions. `TagThrottleKey::toKey()` serializes throttle type, priority, and tag list under `tagThrottleKeysPrefix`. `TagThrottleKey::fromKey()` reverses that format. `TagThrottleValue::fromValue()` decodes the value with the protocol version that includes throttle reason.

## Control flow
Adding a tag enforces knob limits for maximum tag length and maximum tags per transaction, copies the tag into the set arena, and increments byte accounting only for new tags. Key encoding writes the system prefix, one byte for throttle type, one byte for priority, then each tag as one length byte plus tag bytes. The current implementation asserts exactly one tag per throttle even though the wire format has a tag-list shape.

## State and persistence behavior
Throttle records are persisted under the system throttled-tags keyspace declared in `SystemData.cpp`. The encoded key is part of the durable API used to view or control tag throttling. `TagSet` itself is in-memory arena state attached to requests or throttle operations.

## Dependencies and integration points
It depends on `SystemData.h` for key prefixes, `TagThrottle.h` for tag/throttle types, `CLIENT_KNOBS` for validation limits, and Flow binary serialization for values. It integrates with transaction tagging, manual or automatic throttling management, and system-key clients that scan throttled tag records.

## Risks and edge cases
The length and count fields are single bytes, so knob assertions require both limits to remain below 256. `TagSet::toString()` asserts non-empty. The key format claims sorted tags but `TagSet` only deduplicates insertion order in this file; callers must not rely on multi-tag support because `toKey()` asserts `tags.size() == 1`. Malformed throttle keys can be decoded without explicit bounds checks beyond normal memory assumptions.

## Test signals
The local `TEST_CASE("TagSet/toString")` covers singular/plural rendering and capitalization. Additional useful tests are tag limit exceptions, duplicate tag byte accounting, throttle key round trips for automatic/manual types and priorities, malformed key rejection behavior, and value decode compatibility with reason-bearing protocol versions.
