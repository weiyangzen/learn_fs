# sources/user-network-fs/samba/source3/include/util_sd.h

## Purpose
`util_sd.h` declares command/client-facing helpers for converting, parsing, and printing Windows security descriptor components.

## Important APIs, Types, and Functions
- SID conversion: `SidToString` and `StringToSid`.
- ACE formatting/parsing: `print_ace` and `parse_ace`.
- Security descriptor printing: `sec_desc_print`.

## Control Flow and State
The functions operate on `cli_state`, `dom_sid`, `security_ace`, and `security_descriptor` inputs. Conversion and parsing routines transform between textual forms and binary security structures, while print helpers write to a `FILE *`.

## Persistence Behavior
No direct persistence. Printed descriptors can be consumed by tools or logs; parsed ACEs/descriptors may later be applied to filesystem or registry security state by callers.

## Dependencies and Integration Points
It is used by Samba client/admin utilities and ACL tooling that need human-readable SIDs, ACEs, and descriptors. It depends on security NDR types and client connection state for name resolution when `numeric` is false.

## Risks
- Name lookup through `cli_state` can fail or be ambiguous; numeric mode must remain reliable.
- ACE parser strictness affects CLI interoperability and error reporting.
- Printing/parsing must preserve security-relevant fields such as flags, masks, trustee SID, and ACE type.

## Test Signals
Round-trip tests for ACE and SID strings, numeric versus resolved-name printing, malformed ACE parse failures, and descriptor output comparisons.
