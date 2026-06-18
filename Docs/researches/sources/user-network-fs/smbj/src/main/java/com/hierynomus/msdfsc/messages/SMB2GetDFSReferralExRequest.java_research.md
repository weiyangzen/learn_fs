# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralExRequest.java

Source read signal: reviewed complete local file (73 lines, 2197 bytes).

## Purpose
`SMB2GetDFSReferralExRequest.java` covers DFS referral EX request encoder. builds an extended DFS referral request with max referral level, request flags, request filename, and optional site name.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructors initialize path/site fields; `writeTo()` emits request metadata and UTF-16 strings into `SMBBuffer`.

## State and persistence
State is a request DTO until encoded.

## Dependencies and integration points
Integrates with SMB2 IOCTL FSCTL_DFS_GET_REFERRALS_EX call sites.

## Risks
String length/offset accounting is the main interoperability risk; request flags are internal enum values.

## Test signals
Signals are wire-format tests against Windows/Samba referrals.
