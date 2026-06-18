# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfs.hh

## Purpose

`XrdOfs.hh` declares the public and protected class surface for the OFS filesystem adapter. It defines concrete `XrdSfsDirectory`, `XrdSfsFile`, and `XrdSfsFileSystem` implementations and centralizes configuration members, role flags, forwarding specifications, plugin pointers, POSC state, checksum state, and helper declarations used by implementation files.

## Important APIs, Types, and Functions

- `XrdOfsDirectory` implements the SFS directory interface with `open`, `nextEntry`, `close`, `autoStat`, `copyError`, and `FName`. It owns a path string, `XrdOssDF *dp`, EOF state, and a fixed entry buffer.
- `XrdOfsDirFull` wraps `XrdOfsDirectory` with an owned `XrdOucErrInfo` for normal object allocation.
- `XrdOfsFile` implements the SFS file interface. It exposes open/close, clone, checkpoint, fctl, mmap, page read/write, sync and async read/write, readv, stat, sync, truncate, and compression-info methods.
- `XrdOfsFile` state includes request user identity, current `XrdOfsHandle *oh`, optional `XrdOfsTPC *myTPC`, optional `XrdOucChkPnt *myCKP`, raw-I/O flag, destructor-close marker, and checkpoint-bad flag.
- `XrdOfsFileFull` wraps `XrdOfsFile` with owned `XrdOucErrInfo`.
- `XrdOfs` implements `XrdSfsFileSystem`. Public methods allocate file/directory objects and expose filesystem operations: checksum, chmod, connect/disconnect, exists, file attributes, FSctl/fsctl, stats, version, mkdir, prepare, rem/remdir, rename, stat variants, truncate, and configuration.
- The `Options` bit enum models authorization, xattr plugin, roles, forwarding, TPC, subcluster, and TPC redirect flags.
- `fwdOpt` stores forwarding command, host, and port for metadata operations and owns a `Reset()` method.
- Protected helpers include `ConfigXeq`, `Emsg`, `EmsgType`, `fsError`, `Split`, `Stall`, `Unpersist`, and `WaitTime`.
- Private configuration helpers include POSC, redirection, TPC, role, trace, xattr, notification, forwarding, export, and creation-mode parsers.

## Control Flow and Contracts

The header shows the intended layering: protocol-facing `XrdSfs*` methods are public; common error and stall behavior is protected; parser/configuration helpers and plugin state are private. `XrdOfs` grants friendship to file and directory objects so they can use configured authorization, OSS, finder, event, POSC, checksum, and error helpers without a large public API.

Object allocation is split between calls that allocate an owned error-info object (`newDir(char*, int)`, `newFile(char*, int)`) and calls that bind to an existing `XrdOucErrInfo`. This distinction matters for lifetime and monitoring IDs.

## State and Persistence Behavior

The declaration captures persistent runtime state rather than on-disk formats. POSC state is represented by `poscQ`, `poscLog`, `poscHold`, `poscSync`, and `poscAuto`; checkpoint state is only per-file (`myCKP`/`ckpBad`) and configured elsewhere. Creation masks `dMask` and `fMask` persist after configuration and are used by mkdir/chmod/open. `dummyHandle` is a sentinel shared by unopened files. `ocMutex` serializes handle assignment and close/open transitions.

`ConfigFN`, `myRole`, redirect hosts, plugin pointers, and CMS pointers are owned as process-lifetime configuration state. The destructor is intentionally empty because deleting the full plugin graph is considered too complex.

## Dependencies and Integration Points

The header depends on `XrdSfsInterface`, `XrdCmsClient`, `XrdOfsHandle`, `XrdOfsEvr`, `XrdOucCloneSeg`, and `XrdSysPthread`, while forward-declaring most plugin classes. It is the central include for `XrdOfs.cc`, `XrdOfsConfig.cc`, FSctl/file-attribute implementations, and any code that needs the concrete OFS filesystem class.

## Risks and Edge Cases

- Many members are raw pointers with process-lifetime ownership; configuration failure paths must avoid leaks that affect later startup attempts.
- `XrdOfsFile` destructor closes if `oh` is set, so code must handle close side effects during object destruction.
- `fwdOpt::~fwdOpt()` does not free `Host`; cleanup is explicit through `Reset()` or replacement in parsers.
- Role flags use overlapping bit masks (`isPeer`, `isProxy`, `isManager`, `isServer`, `isSuper`, `isMeta`), so parser and role-display logic must preserve intended combinations.
- The class exposes configuration fields publicly for historical/implementation convenience, increasing coupling across files.

## Test Signals

Compilation tests should cover inclusion order and forward declarations. Runtime tests should allocate both owned-error and external-error file/dir objects, verify sentinel handle behavior before open, exercise destructor close, validate configuration masks/role bits after parser directives, and ensure private helper declarations remain consistent with implementations in `XrdOfs.cc` and `XrdOfsConfig.cc`.
