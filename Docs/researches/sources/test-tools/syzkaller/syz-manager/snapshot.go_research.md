## sources/test-tools/syzkaller/syz-manager/snapshot.go

This file implements syz-manager snapshot execution mode. `snapshotInstance` marks a VM as fuzzing and calls `snapshotLoop`. `snapshotLoop` copies the executor, starts it in snapshot mode with logs to `/dev/kmsg`, then repeatedly pulls requests from a distributed source, performs one-time snapshot setup, runs requests against the VM snapshot, detects crashes, and completes queue requests.

`snapshotSetup` sends a flatbuffer handshake with coverage, pointer-size, slowdown, timeout, feature, env flag, and sandbox data. `snapshotRun` serializes a program, sends a flatbuffer request, parses executor output, normalizes call info length by filling errno 999 for missing calls, merges extra coverage/signal arrays, and returns a `queue.Result`. `parseExecResult` handles short buffers, flatbuffer parse errors, and wrong message types as execution errors rather than infrastructure panics.

State is in VM snapshot machinery, manager stats, crash channel, and queue result callbacks. Integration points are `MachineChecked` snapshot branch, flatrpc executor protocol, VM `RunSnapshot`, and fuzzer queue. Risks include panicking if env flags change, continuing after corrupted executor result as program failure, and needing executor/VM support for snapshot mode. No direct tests were observed.
