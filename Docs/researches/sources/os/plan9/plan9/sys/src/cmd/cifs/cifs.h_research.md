# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/cifs.h

Central CIFS header. Defines SMB command IDs, transaction subcommands, flags/capabilities, DFS flags, share/security/file attribute constants, info levels, server enumeration masks, and core structs.

Important structs: `Auth`, `Session`, `Pkt`, `Share`, `FInfo`, RAP info records, `Refer`, and `Fileinfo`. It also declares global runtime state (`Sess`, `Shares`, `Ipc`, `Debug`, etc.) and every cross-file function prototype for auth, packet packing, NetBIOS, RAP, Trans2, NT transactions, DFS, info files, and ping.

This is the subsystem contract; most implementation files depend on it.
