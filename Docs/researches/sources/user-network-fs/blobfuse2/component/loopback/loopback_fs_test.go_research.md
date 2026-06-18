## sources/user-network-fs/blobfuse2/component/loopback/loopback_fs_test.go

Purpose: Test suite for the loopback component's local filesystem implementation.

Important APIs and flow: `SetupTest` constructs a `LoopbackFS`, creates `/tmp/blobfuse2lfstests` with directories and seed files, writes lorem content, and starts the component. Tests validate directory creation/deletion/listing/rename, file creation/deletion/open/read/write/truncate/release, buffered reads with offsets, `GetAttr`, staged block data plus commit, and committing an empty block list to truncate an existing file.

State and persistence: The suite uses a fixed `/tmp/blobfuse2lfstests` path and a separate expanded `~/blocklfstest` path for block tests; cleanup removes these directories. Tests assert actual file metadata and content on disk.

Dependencies and integration: Uses `internal` option structs, `common.ExpandPath`, `stretchr/testify` suite/assert, and the real OS filesystem rather than mocks.

Risks and test signals: The fixed temp path can collide under concurrent runs. There is no explicit test for `Configure`, symlinks, `StreamDir` MD5 mode, `ReadInBuffer` no-handle branch, copy operations, chmod/chown, or error handling. The positive path coverage is strong enough to prove loopback can back xload tests.
