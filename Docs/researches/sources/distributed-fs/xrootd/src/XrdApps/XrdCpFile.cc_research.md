<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.cc

Purpose: implements `XrdCpFile`, a small parsed-file descriptor used by `xrdcp` configuration to classify source/destination operands, resolve local metadata, and expand recursive local directories.

Important APIs/types/functions: constructor parses protocols and normalizes paths; alternate constructor wraps filesystem-walk entries; `Extend()` recursively indexes local files under a directory using `XrdOucNSWalk`; `Resolve()` stats local paths and classifies regular files, directories, `/dev/null`, and `/dev/zero`; static `mPfx` controls namespace-walk message prefix.

Control flow: construction strips trailing slashes except root-like forms, treats `-` as stdio, recognizes xroot/xroots/root/roots/http/https/dav/davs/pelican/s3 URLs, handles `file://localhost` and absolute `file://` paths, and defaults other strings to local files. `Resolve()` temporarily removes a CGI query suffix for `stat()`, restores it, and updates protocol/size. `Extend()` walks a directory recursively and appends each returned regular file to a linked list.

State/persistence: stores mutable `Path`, directory offset/length metadata, protocol enum, protocol name, file size, and `Next` pointer. It reads filesystem metadata but writes nothing.

Dependencies/integration: used by `XrdCpConfig`; depends on POSIX `stat`, path string handling, and `XrdOucNSWalk` for recursive local indexing.

Risks/test signals: `ProtName[8]` is too short to store longer protocol names such as `pelican` plus terminator if copied elsewhere, though constructor copies header length minus delimiter. Local CGI stripping mutates `Path` temporarily and assumes restoration on the success/failure path. Tests should cover URL protocol classification, file URL host forms, trailing slash normalization, stdio, directories, special devices, local paths with `?`, recursive expansion offsets, and unsupported file types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpFile.cc -->
