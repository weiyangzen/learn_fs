# sources/test-tools/syzkaller/executor/files.h

Purpose: File discovery and file-content reporting helpers used during runner handshake and glob requests.

Important APIs and control flow: `Glob` wraps libc `glob` with alternate directory functions. Its custom `readdir` filters most symlinks to avoid recursion and escaping the target tree, while allowing selected symlink names such as `self`, `thread-self`, `kmalloc-64`, and cgroup links. It omits directory results and returns files. `ReadFile` opens a file, records existence/error/data in `rpc::FileInfoRawT`, and reads in 4 KiB chunks. `ReadTextFile` formats a path, reads it, and trims trailing newline/NUL. `ReadFiles` expands globs or reads explicit file paths.

State and dependencies: stateless apart from temporary buffers. Depends on POSIX file APIs, `glob`, `dirent`, and flatrpc file info types.

Integration points: runner `Handshake` sends requested host/VM files to the manager; executor `execute_glob` serializes glob results into output shared memory.

Risks and tests: symlink filtering is intentionally heuristic and name-based. `ReadFile` treats `EEXIST` and `ENOENT` as non-existing, while other open errors mark exists with an error string. `test_glob` builds a small directory tree to validate non-recursive file matching, hard-link inclusion, and controlled symlink handling.
