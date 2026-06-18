# File Research: sources/os/plan9/plan9/sys/src/9/boot/embed.c

Embedded paqfs root method.

Key behavior:
- `configembed()` selects a paq file from explicit `sys` path or method default arg.
- `connectembed()` validates `/boot/paqfs` and selected paq file, binds console/proc, forks `/boot/paqfs -iv <paqfile>`, waits for it, and returns pipe fd connected to paqfs.

This supports booting from an embedded archive file served as a filesystem.
