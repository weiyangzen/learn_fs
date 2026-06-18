# sources/security-integrity/cryfs/crates/rustfs/src/tests/mkdir.rs

Purpose: integration-style tests for mkdir through a mounted fuser-backed mock filesystem.

Important APIs: `test_mkdir` fixture helper, `mkdir_return_ok`, path helpers, and nested test modules for arguments and results.

Control flow and state: each test builds a mock low-level filesystem, sets lookup expectations for parent path and target absence/existence, starts a real mounted `Runner`, then uses `FilesystemDriver::mkdir`. The mock expectation checks propagated request info, parent inode, path component name, mode after kernel umask, and returned/error behavior.

Dependencies and integration: uses `rstest`, `mockall`, `nix::Errno`, fuser mount runner, mock helper, and low-level reply types. It exercises backend adapter, FUSE kernel behavior, and low-level API translation.

Risks and tests: coverage is focused on mkdir and path lookup error cases. TODOs note missing umask detail and broader mkdir errno cases. Because it mounts FUSE, test reliability depends on environment support and unmount cleanup.
