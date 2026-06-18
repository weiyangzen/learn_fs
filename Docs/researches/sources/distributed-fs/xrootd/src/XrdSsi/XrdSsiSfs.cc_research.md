# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSfs.cc

## Purpose
`XrdSsiSfs.cc` implements the XRootD filesystem plugin wrapper for SSI. It initializes SSI configuration, exposes the `XrdSfsGetFileSystem2` entry point, routes locate/stat-like requests to SSI provider state, and optionally delegates ordinary filesystem operations to a stacked native filesystem for configured paths.

## Important APIs and Functions
The external entry point is `XrdSfsGetFileSystem2`. Filesystem overrides include `chksum`, `chmod`, `exists`, `fsctl`, `getStats`, `getVersion`, `mkdir`, `prepare`, `rem`, `remdir`, `rename`, two `stat` overloads, `truncate`, plus private `Emsg`, `Split`, and `setFeatures`.

## Control Flow
Initialization stores the native filesystem pointer in global `theFS`, wires logging/tracing/stats, configures SSI, and returns a static `XrdSsiSfs`. Most namespace operations delegate to `theFS` only when `fsChk` is enabled and `FSPath.Find(path)` matches; otherwise they return `ENOTSUP`. `fsctl` handles `SFS_FSCTL_LOCATE` by checking SSI provider resource status and returning this server's network destination through `XrdNetIF`.

## State and Persistence
The plugin uses process-global pointers for provider, native filesystem, network interface, logger, trace, and stats. No persistent state is written. `freeMax` controls retained file/session object limits elsewhere.

## Dependencies and Integration Points
It integrates XrdSfs interfaces, XrdCms locate semantics, `XrdSsiProvider`, `XrdSsiSfsConfig`, `XrdSsiStats`, `XrdNetIF`, `XrdOucErrInfo`, and `XrdSecEntity`. `newDir` and `newFile` allocate SSI-specific directory/file objects declared in the header.

## Risks and Test Signals
Risks include misconfigured stacking causing legitimate filesystem operations to return `ENOTSUP`, locate response formatting, `Split` not null-terminating copied paths after `strncpy`, and static object lifecycle. Tests should cover plugin initialization failure, locate for present/pending/missing resources, path delegation through `fspath`, checksum delegation toggle, stats composition, IPv4/IPv6/hname locate flags, and each unsupported operation error message.
