# sources/sync-backup/casync/src/caprotocol-util.h

## Purpose
`caprotocol-util.h` declares the protocol type-name helper used for frame diagnostics.

## Important APIs, Types, and Functions
It includes `<inttypes.h>` and `caprotocol.h`, then declares `const char *ca_protocol_type_name(uint64_t u);`.

## Control Flow
There is no control flow in the header; it exposes the mapping function to users of the protocol definitions.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Consumers include `caremote.c`. The header depends on protocol constants from `caprotocol.h`.

## Risks
The header has no include guard despite being tiny; repeated inclusion is harmless for this declaration but inconsistent with the rest of the source tree.

## Test Signals
Covered only by build success unless explicit tests are added for the implementation.
