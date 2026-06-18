# sources/user-network-fs/go-fuse/fs/linearraid_linux_example_test.go

Purpose: Linux example demonstrating zero-copy pipe-backed reads by assembling one virtual file from chunk files.

Important types/functions: `linearRaidNode` implements `NodeGetattrer`, `NodeOpener`, and `NodeReader`; `Read` clamps requested range, obtains a `splice.Pair`, grows it, opens each chunk, loads segments with `LoadFromAt`, and returns `fuse.ReadResultPipe`. `Example_linearRaid` creates chunk files with known content, mounts a root with persistent `raid`, reads it, and expects "content matches".

State/dependencies: chunk files persist in temp dir during example; splice pipe resources are returned with `splice.Done` unless transferred.

Risks/test signals: covers pipe `ReadResult` cleanup and multi-chunk boundary logic. Risks include fd leaks on early loop errors and Linux-only splice behavior. The example has output assertion.
