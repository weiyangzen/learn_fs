## sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test_wrapper.go

Purpose: Go/cgo test support for the non-`fuse2` libfuse handler. It creates a `libfuseTestSuite`, configures a `Libfuse` component over a gomock `internal.Component`, and calls exported cgo callback functions directly to validate FUSE-to-component behavior without mounting a live filesystem.

Important APIs and flow: `newTestLibfuse` loads YAML config, constructs `NewLibfuseComponent`, wires the next component, and stores it in global `fuseFS`. Individual helper tests exercise `libfuse_mkdir`, `rmdir`, `create`, `open`, `truncate`, `unlink`, `symlink`, `readlink`, `fsync`, `fsyncdir`, `chmod`, `chown`, `utimens`, and `statfs`. The file also models the C native file object as `fileHandle` so tests can reinterpret `fi.fh` back into a Go `handlemap.Handle`.

State and dependencies: Tests depend on global `fuseFS`, cgo `libfuse_wrapper.h`, gomock expectations against `internal.MockComponent`, and handle allocation through `handlemap`. Configuration flags such as `disable-writeback-cache` and `ignore-open-flags` materially change open-flag normalization.

Risks: The helpers are sensitive to global state and call `cleanupTest` manually; double cleanup patterns make ordering fragile. The unsafe pointer casts must match `native_file_io.h` layout. Test coverage is broad for errno mapping and flag policy but has TODO gaps for `ReadDir` and rename paths.
