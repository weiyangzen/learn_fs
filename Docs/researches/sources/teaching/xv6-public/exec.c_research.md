# File Research: sources/teaching/xv6-public/exec.c

Implements `exec(path, argv)`.

Key behavior:
- Opens and locks the executable inode inside a filesystem transaction.
- Validates ELF header and program headers.
- Allocates a fresh kernel/user page table, loads program segments, and enforces page alignment and overflow checks.
- Allocates a guard page plus user stack page.
- Copies argument strings and argv pointers to the new stack.
- Updates process name, page table, size, trapframe `eip`/`esp`, switches address space, and frees the old VM.

Failure handling:
- Releases inode transaction state and frees the partially built page table.
- Returns `-1` without modifying the process image unless the final commit point has been reached.
