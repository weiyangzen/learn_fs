# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileSystemTest.h

Purpose: base fixture utilities for typed fspp filesystem tests. It abstracts creation of concrete `fspp::Device` instances and provides common load/create helpers and timestamp-state setup.

Important APIs/types/functions: `FileSystemTestFixture::createDevice`, `FileSystemTest`, `resetFilesystem`, `MODE_PUBLIC`, `Load`, `LoadDir`, `LoadFile`, `LoadSymlink`, `CreateDir`, `CreateFile`, `CreateSymlink`, `EXPECT_IS_*`, and atime relation setters.

Control flow: constructor resets the filesystem with `relatime` context. `resetFilesystem` recreates the concrete fixture and device, then installs the requested `fspp::Context`. Load helpers assert `boost::optional` is present before moving out `unique_ref`.

State and persistence behavior: tests operate on a fresh device per reset. Creation helpers mutate parent directories; atime setup methods read current stat, alter times, and persist them through `utimens`.

Dependencies and integration points: depends on GoogleTest, Boost, `cpputils::unique_ref`, fspp `Device/Node/Dir/File/Symlink/OpenFile`, and context timestamp policies.

Risks and test signals: central helper consistency is critical because many tests assume its atime setup creates exact relative relationships by changing nanoseconds only; edge cases around nanosecond underflow/overflow could affect timestamp tests.
