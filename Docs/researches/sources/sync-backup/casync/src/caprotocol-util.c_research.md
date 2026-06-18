# sources/sync-backup/casync/src/caprotocol-util.c

## Purpose
`caprotocol-util.c` provides a small diagnostic helper that maps binary casync protocol frame type constants to human-readable names.

## Important APIs, Types, and Functions
`ca_protocol_type_name(uint64_t u)` switches over every frame type declared in `caprotocol.h`: hello, index, index-eof, archive, archive-eof, request, chunk, missing, goodbye, and abort. Unknown values return `NULL`.

## Control Flow
The function is a straight switch used by logging/debugging paths. It has no side effects.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
It includes `caprotocol-util.h` and `caprotocol.h`. `caremote.c` includes this helper and has commented debug logging that would print frame names.

## Risks
New protocol frame constants require updating this switch or diagnostics will lose names. Returning `NULL` requires callers to tolerate missing names.

## Test Signals
No direct test is visible. A low-cost unit test could assert all known constants map to non-NULL strings and unknown constants map to `NULL`.
