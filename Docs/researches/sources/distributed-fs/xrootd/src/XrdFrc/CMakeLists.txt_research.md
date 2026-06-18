# sources/distributed-fs/xrootd/src/XrdFrc/CMakeLists.txt

## Purpose

This CMake file adds the File Residency Manager client sources to the `XrdServer` target. XrdFrc supplies request-queue, proxy, cluster-id, tracing, utility, xattr, and locking support for file residency/prestage/migration workflows.

## Important APIs, Types, and Functions

`target_sources(XrdServer PRIVATE ...)` lists CID, Proxy, ReqAgent, ReqFile, Trace, Utils, Request, XAttr, and XLock files. There is no independent library or executable in this file.

## Control Flow

During configuration/generation, these files become private sources of `XrdServer`. Build order and linkage are inherited from the server target.

## State and Persistence Behavior

No runtime state is stored by the build file. It controls whether XrdFrc queue/checkpoint code is compiled into `XrdServer`.

## Dependencies and Integration Points

The file integrates XrdFrc with the server build rather than exposing it as a standalone target. Source-level dependencies include XrdOuc, XrdSys, XrdNet, and request queue files.

## Risks and Edge Cases

Because all listed files are private server sources, external consumers cannot link a separate XrdFrc component. Missing a source here can produce unresolved symbols only when related server code is enabled.

## Test Signals

Build tests should verify `XrdServer` compiles and links with all XrdFrc sources and that installation/runtime configurations exercising FRM client features resolve the included symbols.
