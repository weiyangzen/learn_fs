# sources/test-tools/syzkaller/executor/snapshot.h

Purpose: Snapshot-mode executor support for qemu ivshmem based fast restore/execute cycles.

Important APIs and control flow: `FindIvshmemDevices` scans PCI devices for ivshmem vendor/device IDs, distinguishes doorbell and shared input/output regions by resource size, maps registers and shmem, and points `output_data` after `SnapshotHeaderT`. `SnapshotSetup` enables snapshot mode, reads a flatbuffer handshake from ivshmem input, parses normal executor flags, and performs requested feature setup. `SnapshotSetState` writes state and rings the doorbell. `SnapshotStart` pre-creates threads, prefaults output/input/globals/data/coverage memory, waits for parent prefaulting, marks `Ready`, handles first snapshot acknowledgement, then parses a `SnapshotRequest` after restore. `SnapshotDone` serializes final output and marks `Executed` or `Failed`.

State and dependencies: global `ivs` stores doorbell, header, and input pointers. State persists in the ivshmem header and executor globals across snapshot/restore. Linux pkeys can protect output memory.

Integration points: selected by `main exec snapshot`; shares `parse_handshake`, `parse_execute`, `finish_output`, and coverage/thread machinery with normal execution.

Risks and tests: relies on qemu ivshmem layout, resource sizes, busy-wait state transitions, and precise prefault sizes. Missing devices or feature setup failures are fatal. Test signals are snapshot-mode integration tests rather than local unit tests.
