<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_freebsd_test.go -->
# sources/user-network-fs/bazil-fuse/fs/serve_freebsd_test.go

Purpose: FreeBSD-specific adapters for fs package tests comparing stat and statfs results.

Important APIs, types, and functions: defines `platformStatfs` and `platformStat` for `syscall.Statfs_t` and `os.FileInfo`.

Control flow: functions translate platform fields into common `statfsResult` and `statResult` structs used by cross-platform tests.

State and persistence behavior: read-only conversion of syscall data.

Dependencies and integration points: selected on FreeBSD and consumed by shared serve tests.

Risks and test signals: field width and naming differences are the main risk; tests compare normalized results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_freebsd_test.go -->
