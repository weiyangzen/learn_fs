## sources/user-network-fs/go-fuse/fuse/opcode_linux.go

Purpose: Linux-specific registration and dispatch for FUSE `STATX`.

Important APIs/types/functions: `doStatx` parses `StatxIn`, fills `StatxOut`, and calls `RawFileSystem.Statx`. init registers `_OP_STATX` handler with sizes and types.

Control flow: global handler table is extended after generic opcode init and fixed buffer size is rechecked.

State and persistence: global opcode table mutation; no per-request persistent state beyond output filling.

Dependencies and integration: supports Linux statx syscalls through `fuse.Server`, high-level `fs`, and loopback tests.

Risks and test signals: handler size mismatches can corrupt request parsing. `fs/statx_linux_test.go` is the main behavioral signal.
