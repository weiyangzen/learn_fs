## sources/user-network-fs/go-fuse/fs/randomtype_test.go

Purpose: tests that READDIRPLUS fixes directory entry type bits using lookup attributes when `Readdir` returns stale or generic types.

Important APIs/types/functions: `randomTypeTest` implements `NodeLookuper` and `NodeReaddirer`. `Lookup` returns pseudo-random file or directory stable attrs based on CRC32 of the name. `Readdir` returns all entries as directories. `TestReaddirTypeFixup` reads kernel dirents and validates final type bits.

Control flow: mount root, open the directory, use `NewLoopbackDirStream` to parse `getdents`, then compare each entry mode with the deterministic CRC rule.

State and persistence: children are dynamically created by lookup; no durable backing store.

Dependencies and integration: exercises `DirEntryList.FixMode`, `ReadDirPlus`, lookup integration, and loopback directory parsing.

Risks and test signals: catches mismatches between `Readdir` hints and lookup-derived `EntryOut.Attr.Mode`, important for clients relying on `d_type`.
