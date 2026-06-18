# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.hh

## Purpose
`XrdSsiSfs.hh` declares the SSI filesystem plugin class derived from `XrdSfsFileSystem`. It is the server-facing XRootD filesystem adapter that creates SSI directory/file objects and implements or delegates filesystem namespace operations.

## Important APIs and Types
`newDir` returns `XrdSsiDir`; `newFile` returns `XrdSsiFile`. The class overrides checksum, namespace mutation, existence, fsctl, stats, version, prepare, stat, and truncate methods. Static `setMax` controls `freeMax`. Private helpers format errors and split opaque CGI data from paths.

## Control Flow
The header indicates that this class sits in the XrdSfs callout vector. Operations either become SSI-specific calls in `XrdSsiFile`/`XrdSsiDir`, delegate to a previous filesystem, or reject unsupported namespace actions.

## State and Persistence
Only static `freeMax` is declared here; plugin/global state is defined in the `.cc` and config files. There is no per-instance persisted data, and the destructor comments that deletion is intentionally avoided.

## Dependencies and Integration Points
It depends on `XrdSfsInterface`, `XrdSsiDir`, `XrdSsiFile`, `XrdOucEnv`, and security entity types. `XrdSfsGetFileSystem2` constructs and returns the static instance.

## Risks and Test Signals
The class has a broad virtual API surface, so regressions often show as XRootD filesystem behavior changes rather than compile failures. Tests should cover new file/dir allocation, feature bits, delegation to stacked filesystems, and unsupported-operation return codes.
