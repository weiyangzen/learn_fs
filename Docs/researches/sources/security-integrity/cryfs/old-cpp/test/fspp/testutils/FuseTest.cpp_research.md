# sources/security-integrity/cryfs/old-cpp/test/fspp/testutils/FuseTest.cpp

Purpose: implements the `MockFilesystem` constructor/destructor and the `FuseTest` Google Test fixture used by CryFS FUSE integration tests. It centralizes default filesystem mock behavior and supplies helpers that make FUSE-visible files, directories, and file descriptors appear through `lstat`/`fstat`.

Important APIs/functions: `FuseTest::TestFS()` creates a mounted temporary FUSE filesystem; `TempTestFS` owns `TempDir`, `fspp::fuse::Fuse`, and `FuseThread`; static gmock actions `ReturnIsFile`, `ReturnIsFileWithSize`, `ReturnIsFileFstat`, `ReturnIsDir`, and `ReturnDoesntExist` populate `stat` results or throw `FuseErrnoException`.

Control flow: the fixture constructor installs pessimistic `ON_CALL` defaults that throw `EIO` or `ENOENT`, then whitelists `access()` and root metadata. `TempTestFS` starts FUSE in a background thread on construction and stops it in the destructor. Test helpers add repeated expectations for specific paths/descriptors.

State/persistence: state is in-memory only: shared `MockFilesystem`, optional captured `fspp::Context`, temporary mount directory, and static action objects. No persistent files are written except transient mount-directory activity.

Dependencies/integration: depends on gtest/gmock, Boost filesystem, cpp-utils unique/tempdir, and `fspp::fuse::Fuse`. It integrates with the FUSE callback layer by supplying a filesystem factory returning the shared mock.

Risks: defaults intentionally fail, so tests must configure expected operations. Busy FUSE lifecycle issues are delegated to `FuseThread`. Static non-const actions can be affected by global initialization order but are simple constant gmock actions.

Test signals: this is test infrastructure; coverage appears through downstream FUSE tests that mount `TempTestFS` and assert mock calls.
