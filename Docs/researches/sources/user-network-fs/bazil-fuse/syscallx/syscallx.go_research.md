# sources/user-network-fs/bazil-fuse/syscallx/syscallx.go

Purpose: `syscallx.go` preserves a deprecated compatibility package that forwards extended attribute and msync helpers to `golang.org/x/sys/unix`.

Important APIs, types, and functions: Exported wrappers are `Getxattr`, `Listxattr`, `Setxattr`, `Removexattr`, and `Msync`.

Control flow: Each function directly calls the matching `unix` function and returns its result.

State and persistence behavior: The package itself is stateless. The wrapped syscalls can read or mutate filesystem extended attributes or flush memory-mapped data depending on caller inputs.

Dependencies and integration points: Depends only on `golang.org/x/sys/unix`. Comments mark the package and each function deprecated in favor of direct `unix` usage.

Risks: Deprecation comments contain typos saying `unic` in several places. Keeping wrappers may encourage new code to use obsolete APIs, but it preserves compatibility for existing imports.

Test signals: `serve_test.go` uses `unix` directly for xattrs and `Msync`, demonstrating the preferred replacement path rather than this wrapper package.
