# sources/security-integrity/gocryptfs/contrib/statvsfstat/statvsfstat.go

Purpose: This diagnostic compares metadata returned by path-based `stat` and descriptor-based `fstat`.

Important APIs and functions: It opens a path, calls `unix.Stat` and `unix.Fstat`, and prints or compares the returned `Stat_t` values.

Control flow and state: The command observes filesystem metadata and does not mutate files beyond opening descriptors.

Dependencies and integration points: Used to debug FUSE consistency in gocryptfs between lookup/path and open-file metadata paths.

Risks and test signals: Metadata can legitimately change between calls on active files. Signals are matching stable fields for unchanged files and clear display of differences.
