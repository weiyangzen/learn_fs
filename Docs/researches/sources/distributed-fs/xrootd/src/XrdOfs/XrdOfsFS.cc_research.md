# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFS.cc

## Purpose

This file provides the default SFS filesystem factory for OFS. It defines the global `XrdOfsFS` pointer and exports `XrdSfsGetDefaultFileSystem()`, which initializes the standard `XrdOfs` instance and returns it to the XRootD server.

## Important APIs, types, and functions

`XrdOfs *XrdOfsFS` is the global OFS singleton pointer used throughout the OFS implementation. `XrdSfsGetDefaultFileSystem(XrdSfsFileSystem *native_fs, XrdSysLogger *lp, const char *configfn, XrdOucEnv *EnvInfo)` is the plugin entry point expected by the SFS loader.

## Control flow

The factory sets the OFS error prefix and logger, routes tracing to the same logger, then enters a static mutex. If no OFS instance exists, it points `XrdOfsFS` at a static `XrdDefaultOfsFS`, stores a duplicated config filename, and calls `Configure()`. Configuration failure returns null. Later calls return the already configured singleton.

## State and persistence behavior

State is process-global and static: the singleton pointer, static mutex, and static default filesystem object. The config filename string is copied into `XrdOfsFS->ConfigFN`. There is no durable persistence in this file.

## Dependencies and integration points

It depends on `XrdOfs`, `XrdSysError`, `XrdSysTrace`, and `XrdSysPthread`. It is the load-time bridge from XRootD's SFS plugin system into the OFS implementation and logging/tracing globals.

## Risks and test signals

The singleton pattern means failed configuration after `XrdOfsFS` is set can leave a partially initialized global for later calls. The `native_fs` argument is unused here. Tests should cover successful first load, repeated load returning the same instance, configuration failure behavior, logger/prefix setup, and thread-safety under concurrent factory calls.
