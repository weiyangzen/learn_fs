# sources/user-network-fs/libfuse/lib/modules/subdir.c

Purpose: `modules/subdir.c` implements a high-level stackable module that exposes an underlying filesystem subtree as the apparent root by prepending a configured base directory to most paths, with optional absolute symlink rewriting.

Important APIs, types, and functions: `struct subdir` stores `base`, `baselen`, `rellinks`, and the next filesystem. `subdir_addpath` builds underlying paths. Symlink helpers `count_components`, `strip_common`, and `transform_symlink` convert absolute symlink targets under the base into relative links when `rellinks` is enabled. The module wraps the same broad high-level operation set as iconv: getattr/access/readlink, directory ops, create/remove/rename/link, metadata updates, file I/O buffers, statfs, xattrs, locks, bmap, lseek, and optional statx. `subdir_new` parses `subdir=`, `[no]rellinks`, validates a single lower filesystem, normalizes the base with a trailing slash, and registers through `FUSE_REGISTER_MODULE`.

Control flow: Each wrapper prepends the base path to incoming paths, calls the corresponding `fuse_fs_*` operation on `d->next`, then frees the generated path. Operations with two destination paths convert both sides. `symlink` intentionally converts only the link location path, not the symlink target. `readlink` may transform absolute returned links into relative paths based on the link's location below the base.

State and persistence behavior: Module state is limited to the base string, its length, the relink flag, and the downstream filesystem pointer. It does not cache file data or directory entries. All generated paths are per-call allocations.

Dependencies and integration points: It depends on high-level libfuse module APIs and is always listed in `libfuse_sources`. It composes with other modules through the `next` filesystem pointer and `fuse_get_context()->private_data`.

Risks: Path joining is simple and assumes libfuse-normalized absolute paths; unusual null paths are allowed by passing NULL through. Symlink rewriting is subtle and must avoid truncation. The source currently shows extra braces in `subdir_rmdir` and `subdir_flock`, which appear syntactically hazardous. There is no explicit path traversal filtering here; security depends on upstream path normalization and the lower filesystem.

Test signals: Tests should cover mandatory `subdir=` validation, trailing slash normalization, root path mapping to base, two-path operations, nullpath handling, absolute and relative symlink reads with `rellinks` and `norellinks`, insufficient output buffer for transformed links, and compile/build coverage for all wrapped operations including statx when enabled.
