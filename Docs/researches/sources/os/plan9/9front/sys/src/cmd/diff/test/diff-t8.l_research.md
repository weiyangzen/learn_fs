# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t8.l

Large C-source diff fixture based on NetBSD `kern_malloc.c`.

Key behavior:
- Begins with `/*	$NetBSD: kern_malloc.c...`.
- Contains kernel memory allocator code, comments, copyright text, and C function bodies.
- Ends with a closing brace.

Research notes:
- 392-line realistic C source fixture for testing code diffs, repeated braces, comments, and long common subsequences.
