## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmFiles.hh

Purpose: declares the fileset model and directory scanner API shared by XrdFrm purge and migration. `XrdFrmFileset` represents one base file plus recognized sidecar entries; `XrdFrmFiles` is an iterator over filesystem walks that returns those sets.

Important APIs/types: `XrdFrmFileset` exposes sidecar accessors (`baseFile()`, `failFile()`, `lockFile()`, `pinFile()`, `pfnFile()`), path constructors, `dirPath()`, `Refresh()`, `Screen()`, and `setCpyTime()`. It owns `XrdOucNSWalk::NSEnt *File[XrdOssPath::sfxNum]`, xattr wrappers for copy and pin metadata, a shared directory `XrdOucTList`, and linked-list fields `Next`/`Age`. `XrdFrmFiles::Get()` is the public iterator. Its options control recursion, shared directory compression, caller-owned filesets, and copy-time initialization.

State and persistence: the header encodes that file metadata is not copied into a separate durable object; it is represented by live `NSEnt` entries, stat buffers, sidecar suffix slots, and optional xattrs. The shared directory object uses `ival[dLen]` and `ival[dRef]` as implicit layout constants.

Dependencies and integration: the API binds to `XrdOucNSWalk`, `XrdOucHash`, `XrdOucXAttr`, `XrdFrcXAttr`, and `XrdOssPath`. Callers in purge/migrate rely on `NoAutoDel` to take ownership of returned sets.

Risks and test signals: memory ownership is subtle because `NoAutoDel` changes deletion behavior and shared directory buffers use reference counting in `XrdOucTList`. Tests should verify destructor cleanup, shared directory refcounts, `Get(noBase)` behavior, and xattr refresh semantics for old/new compatibility.
