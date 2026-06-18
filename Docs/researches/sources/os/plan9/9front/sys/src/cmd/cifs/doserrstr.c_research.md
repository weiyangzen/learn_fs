# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/doserrstr.c

Provides translation from legacy DOS/SMB error class/code values to human-readable strings. The table is derived from Samba `nterr.h` material and includes GPL notice text.

`DOSerrs` stores combined keys as `(code << 16) | class`, covering DOS, server/network, and hardware error classes. Examples include access denied, file not found, share conflict, invalid TID, pipe errors, disk full, and authentication failure.

`doserrstr(uint err)` identifies the SMB error class from the low byte, scans for a full table match, and returns a static formatted string. Unknown errors are formatted with class plus numeric code.

Used by debug/packet reporting and likely core CIFS RPC error formatting when negotiated packets are not using NT status codes.

Implementation note: returns a static buffer, so callers must consume/copy immediately if reentrancy is a concern.
