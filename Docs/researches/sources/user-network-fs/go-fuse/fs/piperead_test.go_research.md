## sources/user-network-fs/go-fuse/fs/piperead_test.go

Purpose: Linux regression test for short or failing pipe-backed read results. It ensures a `ReadResultPipe` that promises more data than was written does not corrupt the returned content.

Important APIs/types/functions: `pipefailNode` implements `Open`, `Getattr`, and `Read`. `Read` obtains a splice pipe, grows it, writes only `actual` bytes, and returns `fuse.ReadResultPipe(pair, total)` where `total` may exceed available data.

Control flow: test mounts a file whose stat size is `promise` but whose pipe contains fewer bytes, then `os.ReadFile` checks the read result equals `actual`.

State and persistence: node stores `promise` size and `actual` bytes in memory. Kernel caching is enabled through one-second entry and attr timeouts.

Dependencies and integration: depends on Linux build tag, `splice.Get`, `fuse.ReadResultPipe`, and high-level mount plumbing.

Risks and test signals: catches edge cases in pipe/splice result cleanup and EOF handling. Failures may manifest as hangs, `EIO`, or extra bytes if pipe accounting is wrong.
