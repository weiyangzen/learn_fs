# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/fns.h

Declares function prototypes for `cifsd` subsystems.

Key points:
- Declares binary pack/unpack functions.
- Declares error conversion helpers.
- Declares utility functions for logging, remote-name lookup, path building/splitting, hex dumps, time conversions, size/allocation conversions, attribute conversions, hashing, string translation, and SMB string/name packers.
- Declares SMB command dispatcher `smbcmd`.
- Declares share, RAP transaction, tree/fid/search-id, file, find, directory, and idmap APIs.

Dependencies and interactions:
- Shared by all `cifsd` source files.
- Complements structures and constants from `dat.h`.

Research relevance:
- This header exposes the modular boundaries of the CIFS server.
