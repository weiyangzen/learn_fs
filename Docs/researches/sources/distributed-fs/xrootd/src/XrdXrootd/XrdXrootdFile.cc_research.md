# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFile.cc

Purpose: implements xrootd's per-open-file wrapper and per-link file table. It tracks SFS file objects, sendfile and mmap capability, file statistics, AIO freight objects, file lock release, reference serialization, handle allocation, deferred handle reuse, and monitor close accounting.

Important APIs and functions: `XrdXrootdFile::XrdXrootdFile()` initializes stats, discovers sendfile fd support via `fctl(SFS_FCTL_GETFD)`, detects memory mapping with `getMmap()`, and records file size from mmap or `stat()`. `Init()` installs the global lock manager and logger. The destructor resets AIO, waits for outstanding references with `Serialize()`, deletes the SFS file, unlocks the file path, returns deferred handles through `XrdXrootdFileHP`, deletes freight objects, and frees `FileKey`. `Ref()` adjusts active references and wakes serialization waiters. `XrdXrootdFileTable::Add()` allocates file handles from an inline table, an expandable external table, or recycled deferred handles. `Del()` removes or holds a file entry, rolls page-read/write stats into normal read/write counters, reports monitor close events, and optionally defers deletion. `Recycle()` closes every table entry and destroys the table.

Control flow and state: table manipulation is externally serialized at the link level. `heldSpotP` marks a handle reserved for deferred close/reuse. `XrdXrootdFileHP` tracks handles that become reusable only after close callbacks finish. File-level `refCount` protects destructor-time cleanup from active requests.

Dependencies and integration: integrates SFS files, `XrdXrootdFileLock`, `XrdXrootdAioFob`, `XrdXrootdPgwFob`, monitoring, sendfile, mmap, and trace logging.

Risks and test signals: lifecycle is subtle around async close, deferred handles, and outstanding AIO. Tests should cover table growth, handle reuse after async close, monitor accounting, destructor waiting for references, sendfile disabled by fd discovery, mmap size detection, and lock release on all close paths.
