# sources/test-tools/syzkaller/vm/qemu/snapshot_linux.go

## Purpose

`snapshot_linux.go` implements Linux-only QEMU snapshot acceleration support using ivshmem shared memory, an eventfd doorbell, and syzkaller flatrpc snapshot headers.

## Important APIs, Types, and Functions

The `snapshot` struct stores ivshmem listener/connection, doorbell/event/shmem file descriptors, mapped shared memory, input slice, and `flatrpc.SnapshotHeaderT`. Methods include `snapshotClose`, `snapshotEnable`, `snapshotHandshake`, `SetupSnapshot`, and `RunSnapshot`.

## Control Flow

`snapshotEnable` creates memfds for shared memory and doorbell, sizes and mmaps shared memory, maps input/header regions, creates an eventfd, listens on a Unix socket for ivshmem setup, and returns QEMU args enabling migration/snapshot-compatible ivshmem devices. `snapshotHandshake` accepts the ivshmem connection and sends protocol/version, VM id, doorbell, and eventfd descriptors. `SetupSnapshot` writes initial input, coordinates executor handshake state through the shared header, enables QMP `x-ignore-shared`, and saves the `syz` VM snapshot. `RunSnapshot` writes new input, restores the VM snapshot with `loadvm syz`, waits for completion notification via eventfd/header state, and returns result/output.

## State and Persistence Behavior

State is held in file descriptors, a Unix socket, and a shared mmap region. It persists for the lifetime of the QEMU instance and is cleaned by `snapshotClose`. Input and execution status are communicated through shared memory rather than files.

## Dependencies and Integration Points

It depends on Linux `memfd_create`, `eventfd`, Unix sockets with file-descriptor passing, `syscall.Mmap`, `flatrpc` snapshot constants/header layout, QEMU ivshmem, and QMP snapshot/migration commands. `qemu.go` calls these hooks when `env.Snapshot` enables snapshot mode.

## Risks and Test Signals

This code is tightly coupled to QEMU ivshmem behavior and the executor snapshot protocol. Descriptor leaks, mmap lifetime bugs, endian/header mismatches, restore timeouts, and shared-memory races are high-risk. Tests require Linux integration with QEMU snapshot support, fd-passing validation, repeated `RunSnapshot` cycles, timeout/error handling, and cleanup after failed handshake.
