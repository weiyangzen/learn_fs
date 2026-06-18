# sources/test-tools/cthon04/basic/test8.c

Purpose: symlink and readlink correctness test.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/sname. Uses symlink(), lstat(), readlink(), unlink(), S_IFLNK, errno/EOPNOTSUPP.

Control flow: if S_IFLNK is unavailable it prints a not-supported message and completes. Otherwise it enters the test directory, repeatedly creates a symlink name with fname prefix pointing to sname+index, verifies lstat type and readlink byte count/content, then unlinks it.

State and persistence: symlinks are transient and removed in the same iteration; no regular file tree is created.

Dependencies and integration points: depends on Unix symlink APIs; DOS/Win32 builds generally take the unsupported path.

Risks: uses readlink() without null-terminating buf but compares using returned length; absolute default target is intentionally not required to exist; unsupported filesystems are treated as skipped/ok.

Test signals: type mismatch, readlink length/content mismatch, or unlink failure is fatal; success reports operation count and complete().
