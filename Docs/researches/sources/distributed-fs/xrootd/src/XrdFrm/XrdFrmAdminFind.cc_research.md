<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFind.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFind.cc

## Purpose
`XrdFrmAdminFind.cc` implements `frm_admin find` queries over local cache state: failed transfers, mmapped files, missing or stale checksums, pinned files, and unmigrated files.

## Important Functions
`FindFail()` walks transfer fail-file directories and prints paths ending in `.fail`. `FindMmap()` lists files with `XrdFrm.Mem` xattrs and reconstructs `mmap` commands. `FindNocs()` checks a requested checksum type through `XrdCksManager` and reports missing or invalid checksums. `FindPins()` lists active pin xattrs, formats permanent, idle-duration, and until-date pins, and deletes expired until-time pins. `FindUnmi()` reports files without copy time or with mtime newer than copy time.

## Control Flow, State, And Persistence
Find commands are mostly read-only tree walks using `XrdFrmFiles` or `XrdOucNSWalk`, but `FindPins()` mutates state by deleting expired pin xattrs. Each command supports multiple directory arguments after the initial target and updates counts for summary output.

## Dependencies And Integration Points
The file depends on `XrdFrmConfig` for path mapping and checksum manager, `XrdFrmFiles` for fileset traversal, `XrdFrcXAttrMem`/`Pin`, and `XrdOucNSWalk` for fail-file discovery. It is dispatched by `XrdFrmAdmin::Find()`.

## Risks And Test Signals
`FindFail()` assigns additional args to `dirFN` in the loop condition but never assigns `lDir = dirFN`, so multiple directory arguments appear not to be processed correctly. `FindPins()` has side effects during a find operation by deleting expired xattrs. Time formatting changes pins within one week into idle-style output. Tests should cover multiple directory arguments, relocated fail-file directories via `xfrFdir`, unsupported checksum types, expired and active pins, recursive vs non-recursive scans, and checksum manager return codes including `-ESTALE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFind.cc -->
