# `sources/user-network-fs/go-fuse/fuse/server.go`

## Purpose
Implements the main FUSE device server: mount setup, INIT negotiation, request reader concurrency, request memory accounting, dispatch into `protocolServer`, response writes, notifications, cache retrieval, unmount, and wait semantics.

## Important APIs, Types, And Functions
Exports `Server`, `NewServer`, `Serve`, `Wait`, `Unmount`, `WaitMount`, `KernelSettings`, `RecordLatencies`, notification methods, `requestAccountingSizes`, and capability helpers on `InitIn`.

## Control Flow
`NewServer` normalizes options, mounts, reads and handles INIT synchronously, initializes the filesystem, then arms the serve loop. `readRequest` reserves request bytes, reads from `/dev/fuse`, parses headers, and may spawn more readers. `handleRequest` parses typed buffers, dispatches, serializes, and writes unless reply is suppressed.

## State And Persistence
Holds mount fd/path, reader counts, inflight byte accounting, buffer/request pools, kernel settings, notification retrieve table, and wait groups. Unmount closes the device after loops exit and wakes pending cache-retrieve waiters with `ENODEV`.

## Dependencies And Integration Points
Depends on OS mount/unmount helpers, `writev`, `pollHack`, splice support, raw FUSE protocol structs, and `RawFileSystem` handlers.

## Risks And Edge Cases
Concurrency and resource accounting are central risks: readers must be refilled without exceeding `MaxInflightRequestBytes`; writes must not race close; notification retrieval must not leak waiters. INIT/version sizing and errno polarity are protocol-sensitive.

## Test Signals
`server_linux_test.go`, cache-control tests, notify tests, mount tests, and broad loopback integration exercise reader liveness, request limits, notification paths, and unmount behavior.
