# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsDirectory.hh

## Purpose
Defines the directory wrapper used by the stats OSS plugin to time directory listing operations.

## Important APIs and control flow
`Directory` inherits `XrdOssWrapDF`, owns the wrapped `XrdOssDF` in `m_wrappedDir`, and forwards through `wrapDF`. `Opendir()` wraps the call in `FileSystem::OpTimer` using directory-list operation counters and timing fields. `Readdir()` similarly times individual directory entries using the `m_dirlist_entries` counter and the same directory-list timing bucket.

## State, dependencies, and integration
The object holds a copy of `XrdSysError`, a reference to the parent `FileSystem`, and the owned wrapped directory descriptor. It depends on `XrdOucEnv`, `XrdOssWrapper`, and `XrdOssStatsFileSystem`.

## Risks and test signals
The wrapper only instruments open/list operations, leaving other descriptor methods inherited through `XrdOssWrapDF`. Directory tests should verify descriptor ownership, forwarded return codes, and increments to directory operation and slow-operation counters under configured slow thresholds.
