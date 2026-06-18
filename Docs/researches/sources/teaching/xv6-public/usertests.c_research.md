# File Research: sources/teaching/xv6-public/usertests.c

Large user-space regression suite for xv6 process, VM, syscall validation, and filesystem behavior.

Major test areas:
- Filesystem transaction edge cases: `iputtest`, `exitiputtest`, `openiputtest`.
- Basic file operations: open failures, small writes, big file direct/indirect blocks, create/unlink loops, directory creation/removal.
- Pipes/processes: pipe ordering, preemption with CPU-bound children, exit/wait races, shared file descriptor offsets.
- Concurrent filesystem stress: four writers, create/delete races, concurrent create/link/unlink, link/unlink deadlock probing.
- Directory/path semantics: subdirectories, `.`/`..`, `DIRSIZ` truncation, file-vs-dir errors, empty names, large directories using indirect blocks.
- VM and memory: malloc exhaustion/reuse, `sbrk` grow/shrink/reallocate, failed allocation cleanup, kernel memory access protection, BSS zeroing.
- Syscall argument validation: bad integer/string pointers and negative read size.
- Exec argument boundaries: oversized argument vectors.
- User I/O privilege: attempts port I/O from user space.
- Link/unlink behavior: hard links, reading unlinked-but-open files, directory link restrictions.

Main sequence:
- Creates `usertests.ran` to prevent rerun on the same filesystem image.
- Runs a broad ordered suite, ending with `exectest` that execs `echo ALL TESTS PASSED`.

Notable details:
- `fsfull` exists but is not invoked because block exhaustion panics.
- Some tests intentionally rely on process death from traps or kernel validation failures.
