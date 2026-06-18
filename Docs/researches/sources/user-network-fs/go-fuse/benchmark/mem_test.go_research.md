# sources/user-network-fs/go-fuse/benchmark/mem_test.go

Purpose: optional integration benchmark/test that mounts an in-memory go-fuse filesystem and runs `fio` against it.

Important types/functions: `memFile` embeds `fs.MemRegularFile`, suppresses xattr security probes with `ENOSYS`, and returns OK from `Fsync`; `memDir.Create` creates a `memFile` inode and adds it as a child; `TestBenchmarkMemFSFio` locates `fio`, mounts the fs with long attr/entry timeouts, then runs a 1 GiB direct-read fio workload.

Control flow/state: created files are in-memory slices; the mount is cleaned up through `t.Cleanup`.

Dependencies/integration: requires `fio`, FUSE mount capability, and `fs.Mount`. Risks include high resource use, direct I/O behavior, and test flakiness under constrained CI; it skips if `fio` is absent.
