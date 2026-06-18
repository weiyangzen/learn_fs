<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.hh

Purpose: declares the `XrdCpFile` linked-list node used to represent parsed copy operands for `xrdcp`.

Important APIs/types/functions: `PType` enumerates `isOther`, `isDir`, `isFile`, `isStdIO`, `isXroot`, `isXroots`, `isHttp`, `isHttps`, `isPelican`, `isS3`, `isDevNull`, and `isDevZero`; public fields include `Next`, `Path`, `Doff`, `Dlen`, `Protocol`, `ProtName`, and `fSize`; methods are `Extend()`, `Resolve()`, `SetMsgPfx()`, constructors, and destructor.

Control flow: callers create nodes while parsing operands, call `Resolve()` for local paths, optionally call `Extend()` for recursive directories, then traverse the `Next` chain to schedule copy work.

State/persistence: owns `Path` memory and frees it in the destructor. No durable state.

Dependencies/integration: integrated with `XrdCpConfig` and copy execution code that interprets directory-offset fields when constructing destination paths.

Risks/test signals: public mutable fields permit accidental ownership or protocol changes. The linked-list ownership model requires exactly one owner to delete each node. Tests should verify constructors initialize all fields, destructor frees duplicated paths but not externally moved namespace-walk paths incorrectly, and recursive path metadata is preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.hh -->
