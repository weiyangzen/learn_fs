# sources/security-integrity/encfs/tests/xattr_test.rs

Purpose: verifies extended attribute support through `EncFs`: setting, getting, listing, removing, on-disk name prefixing, binary/empty/unicode values, and round trips.

Important APIs/types/functions: `setup_fs`, `req`, `create`, `release`, `setxattr`, `getxattr`, `listxattr`, `removexattr`, and `fuse_mt::Xattr`. `test_xattr_on_disk_storage` uses libc `llistxattr` and `OsStrExt` to inspect backing attributes.

Control flow: tests create a file, apply multiple xattrs in namespaces such as `user`, `security`, and `trusted`, retrieve data, parse null-separated list output, remove attrs, and verify absence. The disk-storage test checks raw backing xattr names start with `user.encfs.`. The round-trip test includes binary bytes, empty values, and UTF-8 bytes.

State and persistence: writes xattrs to temporary encrypted backing files and removes temp roots.

Dependencies and integration points: depends on OS xattr support, permissions for non-user namespaces, encrypted xattr naming/value logic, and FUSE xattr response conventions.

Risks: `security.*` and `trusted.*` attributes may require privileges or be unsupported on some filesystems. The test assumes xattr APIs are available and that `getxattr(..., size=0)` returns data, not only size.

Test signals: broad coverage for xattr translation and cleanup, with an extra privacy signal that raw names are stored under an EncFS-specific prefix.
