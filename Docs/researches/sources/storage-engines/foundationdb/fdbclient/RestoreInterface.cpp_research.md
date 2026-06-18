# sources/storage-engines/foundationdb/fdbclient/RestoreInterface.cpp

## Purpose
`RestoreInterface.cpp` defines the system keys and serialization helpers used to store and trigger restore requests in FoundationDB system keyspace.

## Important APIs, Types, and Functions
- `restoreRequestDoneKey` marks restore request completion state.
- `restoreRequestTriggerKey` stores the trigger value for restore workers.
- `restoreRequestKeys` is the range containing indexed restore request records.
- `restoreRequestTriggerValue(UID randomID, int numRequests)` serializes request count and random ID with `ProtocolVersion::withRestoreRequestTriggerValue()`.
- `decodeRestoreRequestTriggerValue(ValueRef const&)` reads the request count and random ID, returning only the count.
- `restoreRequestKeyFor(int index)` appends a binary index to the restore request key prefix.
- `restoreRequestValue(RestoreRequest const&)` serializes the full request with `ProtocolVersion::withRestoreRequestValue()`.

## Control Flow and State
The helpers are straight-line serialization/deserialization routines. Key construction uses an unversioned writer for the binary key suffix, while values include explicit protocol versions for compatibility.

## State and Persistence Behavior
The persistent state is the system keyspace data under `\xff\x02/restoreRequest...`. This file defines how restore requests and triggers are encoded into keys/values that other restore components consume.

## Dependencies and Integration Points
The file includes `RestoreInterface.h` and `flow/serialize.h`. It integrates with restore orchestration code that writes trigger keys and individual indexed requests, and with workers that read/decode them.

## Risks and Edge Cases
- The header declares `decodeRequestRequestTriggerValue`, but the implementation defines `decodeRestoreRequestTriggerValue`; that name mismatch should be checked against callers and build coverage.
- Serialization format changes require protocol-version updates and downgrade planning, as noted in the request type.
- Binary key encoding must remain stable because restore workers locate requests by index.

## Test Signals
Useful tests should round-trip trigger values and `RestoreRequest` values across protocol versions, validate indexed key ordering, check the declared/defined decode function name, and verify system key range boundaries.
