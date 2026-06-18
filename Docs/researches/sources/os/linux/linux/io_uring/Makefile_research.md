# File Research: sources/os/linux/linux/io_uring/Makefile

## Purpose
Builds the io_uring subsystem objects according to kernel configuration.

## Main Contents
- Enables GCOV profiling for io_uring when `CONFIG_GCOV_PROFILE_URING` is set.
- Core `CONFIG_IO_URING` object list includes submission/completion core, opcode definitions, buffers/resources, files, rw, poll, task work, wait, eventfd, uring commands, open/close, sqpoll, xattr, nop, fs ops, splice, sync, msg_ring, advise, statx, timeout, cancel, waitid, register, truncate, memmap, allocation cache, query, and loop.
- Conditional objects: `zcrx.o`, `io-wq.o`, `futex.o`, `epoll.o`, `napi.o`, `net.o`, `cmd_net.o`, `fdinfo.o`, `mock_file.o`, `bpf_filter.o`, `bpf-ops.o`.

## Cross-File Relationships
- Shows which files in this research group are core io_uring objects versus config-dependent support modules.
- `openclose.o` appears twice in the core list, which Kbuild de-duplicates operationally but is worth noticing during maintenance.

## Risks / Review Notes
- Feature boundaries are compile-time; headers in this group provide stub behavior for disabled configs where needed.
