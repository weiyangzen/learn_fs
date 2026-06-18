# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/DFSReferral.java

Source read signal: reviewed complete local file (184 lines, 5376 bytes).

## Purpose
`DFSReferral.java` covers abstract DFS referral entry. parses/writes the common referral header, dispatches versions 1, 2, 3, and 4, holds path/DFS path/alternate/special/expanded-name fields, and exposes server type and entry flags.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Factory peeks at `VersionNumber`, constructs the matching subclass, `read()` consumes common fields then version-specific body and advances to entry size; `writeTo()` writes common fields and delegates offsets/data to subclasses.

## State and persistence
State is one parsed referral entry object with TTL, server type, flags, and optional strings/lists.

## Dependencies and integration points
Integrates with `SMB2GetDFSReferralResponse`, referral caches, and `SMBBuffer` UTF-16 offset parsing.

## Risks
Unknown versions throw `IllegalArgumentException`. Offset handling depends on subclass size math and buffer positions.

## Test signals
Signals are referral parse/write roundtrips and DFS integration tests.
