# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.h

Purpose: declares the CryFS FUSE test fixture and a full Google Mock implementation of `fspp::fuse::Filesystem`.

Important APIs/types: `MockFilesystem` mocks context setup, open/close, stat, truncate, read/write, sync, access, creation/removal, rename, directory reads, timestamps, `statfs`, ownership/mode changes, and symlink operations. `FuseTest` exposes `fsimpl`, `context()`, `TestFS()`, metadata-return helpers, and `OnOpenReturnFileDescriptor()`. Nested `TempTestFS` owns the mounted test filesystem.

Control flow: tests derive from `FuseTest`, configure `fsimpl` expectations, call `TestFS()`, operate on `mountDir()`, and let RAII tear down FUSE.

State/persistence: `FuseTest` keeps a shared mock and optional `fspp::Context`. `TempTestFS` keeps a temporary directory, a `Fuse` object, and the thread wrapper. Lifetime is scoped to the test.

Dependencies/integration: pulls in gtest/gmock, `Filesystem.h`, `FuseErrnoException`, `Fuse`, `Dir`, Boost filesystem, cpp-utils tempdir, and `FuseThread`.

Risks: the mock API mirrors the production filesystem interface, so signature drift breaks many tests. `context()` asserts if FUSE did not call `setContext()`, which is useful but makes initialization ordering visible.

Test signals: no direct tests, but it is the main fixture contract for FUSE behavior tests.
