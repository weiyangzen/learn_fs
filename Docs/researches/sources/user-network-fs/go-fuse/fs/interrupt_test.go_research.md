# sources/user-network-fs/go-fuse/fs/interrupt_test.go

Purpose: verifies kernel interrupt/cancellation can reach a blocked `Open` operation.

Important types/functions: `interruptRoot.Lookup` exposes a `file` inode; `interruptOps.Open` waits either for 100ms and returns `EIO` or for context cancellation and returns `EINTR` while setting `interrupted`; `TestInterrupt` runs `cat` on the file, kills it shortly after start, unmounts, and asserts interruption was observed.

State/dependencies: real FUSE mount and process signaling.

Risks/test signals: valuable for context cancellation semantics but timing-sensitive. The test comment notes it is also investigative for INTERRUPT opcode handling.
