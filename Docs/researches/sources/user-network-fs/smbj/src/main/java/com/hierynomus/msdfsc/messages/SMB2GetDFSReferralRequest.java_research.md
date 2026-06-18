# sources/user-network-fs/smbj/src/main/java/com/hierynomus/msdfsc/messages/SMB2GetDFSReferralRequest.java

Source read signal: reviewed complete local file (36 lines, 1171 bytes).

## Purpose
`SMB2GetDFSReferralRequest.java` covers DFS referral request encoder. builds the standard DFS referral request with max referral level and requested UNC path.

## Important APIs, types, and functions
The important surface is the file's declared workflow, class, enum, or helper methods as described by the source. It is part of the `subset-b-010012` WREPL/SMBJ research slice and was read from the local source tree for this report.

## Control flow
Constructor stores the path; `writeTo()` writes max referral level and UTF-16 request file name.

## State and persistence
State is a simple request DTO.

## Dependencies and integration points
Integrates with SMB2 DFS referral IOCTL code.

## Risks
Path encoding and null termination must match MS-DFSC expectations.

## Test signals
Signals are successful referral responses from Samba/Windows DFS roots.
