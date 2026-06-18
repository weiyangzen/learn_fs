## sources/object-store/minio-mc/pkg/disk/stat_netbsd.go

Purpose: NetBSD implementation of `GetFileSystemAttrs`, mirroring the BSD attribute serialization for mc preserved attributes.

Control flow calls `syscall.Stat`, formats `Atimespec` and `Mtimespec`, appends numeric UID/GID and optional resolved user/group names. State is read-only filesystem metadata. Dependencies are syscall and user lookup APIs. Integration is the same metadata path used by copy/archive commands that preserve filesystem attributes. Risks are platform-specific compile/runtime coverage, silent name omissions, and delimiter collisions in user/group names. No direct NetBSD test is present in the subset, so build-matrix coverage is the main signal.
