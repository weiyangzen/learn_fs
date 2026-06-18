# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/cifs.h

Defines the shared protocol vocabulary and cross-module API for the Plan 9 CIFS client/server bridge. It contains SMB command IDs, Trans2/NT transaction subcommands, negotiated flags/capabilities, DFS flags, share types, file attribute/access/create constants, and info-level constants.

Core data structures include `Auth`, `Session`, `Pkt`, `Share`, `FInfo`, RAP result structs, DFS `Refer`, workstation/file info structs, and global state declarations such as `Sess`, `Shares`, `Nshares`, `Ipc`, `Host`, `Debug`, and `Active`.

The `Session` struct captures negotiated transport/authentication state, server capabilities, packet-signing state, timing, locks, and remote identity. `Pkt` is the mutable packet cursor object used by all SMB/transaction pack/unpack code.

The header also declares the functional boundaries across the CIFS implementation: authentication, SMB core RPCs, DFS mapping, info-file generation, NetBIOS transport, byte packing, ping/RTT support, RAP enumeration, Trans2 file/FS operations, NT security descriptor query, and SID-to-name augmentation.

Notable implementation context: this is an SMB1/CIFS-era client with optional NetBIOS transport, NT SMB capabilities, DFS support, RAP administrative queries, Unicode path support, and Plan 9 9P-facing synthetic filesystem behavior.
