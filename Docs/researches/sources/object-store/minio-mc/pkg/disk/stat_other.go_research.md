## sources/object-store/minio-mc/pkg/disk/stat_other.go

Purpose: OpenBSD/Solaris implementation of `GetFileSystemAttrs` selected by `//go:build openbsd || solaris`. It serializes stat metadata using `Atim` and `Mtim` fields.

Control flow is equivalent to the Linux/BSD variants: stat file, append times, numeric IDs, optional names, and mode into the slash-separated attribute string. State is read-only filesystem metadata. Dependencies are `syscall`, `os/user`, and formatting packages. Integration is cross-platform preserved attribute support. Risks include platform struct differences, silent lookup failure, and no direct tests on these less-common targets. The build tag itself is a key integration point because unsupported platforms must either use this file or provide another implementation.
