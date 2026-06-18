# sources/sync-backup/bup/test/int/test_metadata.py

Purpose: tests metadata path sanitization, archive/extract safety checks, metadata capture from saved archives, restricted-access error recording, restore-over-existing behavior, Linux xattr cleanup, and maximal metadata hashing.

Important APIs/types/functions: `metadata._clean_up_path_for_archive`, `_risky_path`, `_clean_up_extract_path`, `metadata.from_path`, `Metadata.apply_to_path`, `Metadata.create_path`, `metadata.xattr`, `helpers.clear_errors`, `detect_fakeroot`, `is_superuser`, `LocalRepo`, `vfs.resolve`, `vfs.contents`, `setup_testfs()`, and `cleanup_testfs()`.

Control flow: path tests enumerate absolute, relative, dot, parent, slash, and empty cases. `test_metadata_method()` creates a directory with a file and symlink, sets nanosecond mtimes, runs `bup init/index/save`, opens the repository, resolves the saved path, and validates metadata for the directory, file, and symlink. Restricted-access tests chmod paths to `000` and assert saved error prefixes. Restore tests alternate directory/file metadata over existing file, directory, and non-empty directory targets. Linux-only tests mount a loop ext filesystem with ACL/xattr support and verify xattr replacement and hashability with optional `attr`, `setfacl`, and `chattr`.

State and persistence behavior: creates bup repositories, files, symlinks, loopback filesystem images, mount points, xattrs, ACLs, Linux attributes, and saved error global state. It deliberately mutates permissions and relies on cleanup/finally blocks to clear errors and unmount/remove test images.

Dependencies/integration points: depends on Linux mount tools for privileged tests, bup CLI commands, Git repository checks, VFS resolution, metadata serialization, xstat timestamp wrappers, and optional xattr/ACL/attr tools.

Risks and test signals: several tests skip under superuser, fakeroot, Cygwin, non-Linux, or missing mount support. The risk surface is high because metadata restore can overwrite filesystem objects; tests isolate in `tmpdir` and a hidden `testfs`. Signals include exact sanitized path outputs, expected error counts/prefixes, preserved symlink metadata, and correct xattr replacement.
