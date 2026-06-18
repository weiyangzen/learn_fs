# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/all.h

Purpose: umbrella include for 9nfs.

Key behavior: includes Plan 9 base libraries, auth/fcall/regexp, local `dat.h`, `fns.h`, `rpc.h`, and `nfs.h`, and vararg format checks for logging helpers.

Integration notes: most 9nfs implementation files include this single header to share all protocol and utility definitions.
