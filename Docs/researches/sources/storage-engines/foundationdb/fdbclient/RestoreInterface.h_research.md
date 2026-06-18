# sources/storage-engines/foundationdb/fdbclient/RestoreInterface.h

## Purpose
`RestoreInterface.h` declares the wire/storage contract for restore requests and replies. It defines serializable request/reply types plus system keys used to coordinate restore work.

## Important APIs, Types, and Functions
- `RestoreCommonReply` carries the replying server `UID` and an `isDuplicated` flag.
- `RestoreRequest` carries request index, backup tag, URL, optional proxy, target version, key range, random UID, prefix rewrite fields, and a reply promise.
- Both structs define `file_identifier` constants and Flow `serialize` methods.
- `toString` methods provide diagnostic output for tracing or logs.
- Extern keys identify done, trigger, and request ranges.
- Helper declarations cover trigger value encode/decode, per-index request keys, and request value serialization.

## Control Flow and State
This header is declarative. Restore clients construct `RestoreRequest` values, serialize them into system keyspace, and receive `RestoreCommonReply` asynchronously through `ReplyPromise`.

## State and Persistence Behavior
`RestoreRequest` values are persisted as serialized values under the restore request system-key prefix. Fields such as `targetVersion`, `range`, `addPrefix`, and `removePrefix` define how restored backup keys are transformed and bounded.

## Dependencies and Integration Points
The header depends on `FDBTypes.h` for keys, ranges, versions, and UIDs, and `fdbrpc/fdbrpc.h` for reply promises. It is part of the interface between restore coordinators and restore-capable server actors.

## Risks and Edge Cases
- The constructor takes `Key& addPrefix` non-const while storing by value, which is unnecessarily restrictive for callers.
- Comments warn that serialization changes require `ProtocolVersion::RestoreRequestValue` updates and downgrade consideration.
- Prefix rewrite semantics with both add and remove prefixes are not fully covered by simulation according to the inline comment.
- The declared decode helper name appears inconsistent with the `.cpp` implementation.

## Test Signals
Tests should cover serialization compatibility, duplicate reply formatting, prefix rewrite combinations, optional proxy handling, request key generation, and declaration/definition linkage for the decode helper.
