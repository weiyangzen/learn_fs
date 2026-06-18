# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_filesystem.py

Purpose: filesystem-oriented matchers for path existence, file/dir type, directory listings, file contents, permissions, canonical path equality, and tarball contents.

Important APIs, types, and functions: factory matchers `PathExists()`, `DirExists()`, and `FileExists()` wrap filesystem predicates. Classes `DirContains`, `FileContains`, `HasPermissions`, `SamePath`, and `TarballContains` perform richer checks.

Control flow: directory and file-content matchers first check path existence/type, then read listings or file contents and delegate to configured matchers. `HasPermissions` compares the last four octal mode digits. `SamePath` compares `abspath(realpath(...))`. `TarballContains` opens the tarball and compares sorted member names.

State and persistence: matchers read live filesystem and tarball state but do not write. File handles are explicitly closed.

Dependencies and integration points: depends on `os`, `tarfile`, basic and higher-order matchers. Used by test suites needing filesystem assertions.

Risks and test signals: `FileContains.__str__` references `self.contents`, which is never assigned, so stringifying that matcher can raise `AttributeError`. File reading uses default text encoding. Test signals include missing path diagnostics, listing equality, symlink normalization, permission strings, and tarball file closure.
