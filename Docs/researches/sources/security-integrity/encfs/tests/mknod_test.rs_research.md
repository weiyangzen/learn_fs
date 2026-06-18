# sources/security-integrity/encfs/tests/mknod_test.rs

Purpose: verifies `EncFs::mknod` supports FIFO creation and reports named-pipe type correctly through `getattr` and `readdir`.

Important APIs/types/functions: `setup_fs` creates an `EncFs` with deterministic AES-192 key/IV and `EncfsConfig::test_default`. `req` creates a static `RequestInfo`. Tests use `FilesystemMT::mknod`, `getattr`, and `readdir`. `S_IFIFO` encodes POSIX FIFO mode.

Control flow: `test_mknod_fifo_getattr_returns_named_pipe` creates a FIFO, checks FUSE attributes for `FileType::NamedPipe` and permission bits, then inspects the encrypted backing entry with Unix `FileTypeExt::is_fifo`. `test_mknod_fifo_readdir_reports_named_pipe` creates a FIFO and asserts the plaintext virtual directory entry reports `NamedPipe`.

State and persistence: creates temporary root directories and backing FIFO nodes, then removes them.

Dependencies and integration points: depends on Unix FIFO support, encrypted name translation in `EncFs`, and metadata-to-FUSE file type mapping.

Risks: Unix-only behavior; special node creation may require platform support and could behave differently under restricted filesystems. The test only covers FIFOs, not block or character devices.

Test signals: guards special-file type preservation through creation, metadata, and directory listing.
