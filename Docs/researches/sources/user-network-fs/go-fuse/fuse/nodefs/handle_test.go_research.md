## sources/user-network-fs/go-fuse/fuse/nodefs/handle_test.go

Purpose: unit tests for portable handle map behavior.

Important APIs/types/functions: `markSeen` checks panic messages. Tests cover lookup counts, basic register/decode/forget, multiple objects, generation changes after reuse, and known generation behavior.

Control flow: tests register `handled` objects, call map operations, assert counts and decoded pointers, and verify panics for invalid double registration.

State and persistence: in-memory handle maps only.

Dependencies and integration: validates `handle.go`, which protects nodefs inode/file lifetime semantics.

Risks and test signals: failures here indicate potential stale inode/file handle reuse visible to the kernel.
