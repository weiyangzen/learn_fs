# sources/user-network-fs/blobfuse2/common/util_test.go
## sources/user-network-fs/blobfuse2/common/util_test.go

Purpose: broad test coverage for common utility functions.

Important APIs/helpers: `utilTestSuite`, shared `randomString`, and tests for bitmaps, mount detection, directories, encryption, path expansion, usage, cleanup, file writing, checksums, FUSE version parsing, pipeline helpers, open flag formatting, goroutine IDs, and `SetFrsize`.

Control flow: tests exercise concurrent `BitMap64` operations, deterministic set/clear/reset semantics, shell out to `../blobfuse2` for mount-active cases, create temporary loopback mount configs, create/delete directories and files, encrypt/decrypt random data, expand multiple path forms including Azure special containers, measure disk usage after writing MB-sized files, and validate pipeline conflict rules.

State and persistence: creates directories under the user's home and working directory, writes `config.yaml`, `abc.txt`, `.blobfuse2/test_*.txt`, and temporary mount directories, changes working directory during mount tests, and invokes real mount/unmount commands.

Dependencies/integration: requires built `../blobfuse2`, FUSE support, `pidof`, `du`, `fusermount3`, home directory write access, and Linux system behavior.

Risks: environment-sensitive integration tests can fail without FUSE or the binary. Some tests use `typesTestSuite` receiver methods in this file, relying on another suite type in the same package, which is legal but surprising. File cleanup is mostly manual and can leave artifacts on assertion failure. `DecryptData` too-short ciphertext panic is not tested.

Test signals: strong mixed unit/integration signal for utility behavior and known external dependencies.
