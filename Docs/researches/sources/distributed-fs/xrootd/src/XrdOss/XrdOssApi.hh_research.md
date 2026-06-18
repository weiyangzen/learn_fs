# sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.hh

## Purpose

`XrdOssApi.hh` declares the default OSS concrete classes: `XrdOssDir`, `XrdOssFile`, and `XrdOssSys`. It extends the public OSS interface with implementation state, configuration hooks, cache/stage/MSS helpers, and default storage behavior.

## Important APIs, Types, and Functions

`XrdOssDir` implements `Close`, `Fctl`, `Opendir`, `Readdir`, `StatRet`, and `getFD`, and stores local/MSS directory handles, stat-return pointer, EOF/open flags, and directory options. `XrdOssFile` implements clone, open/close, chmod/control, sync/truncate/stat, mmap/compression introspection, byte/vector/raw/async I/O, and stores FD-related cache/mmap/compression state. `XrdOssSys` implements the filesystem methods from `XrdOss` plus `Configure`, config display, staging, stat variants, MSS methods, stats, `AioInit`, name-to-name mapping, path options, and many protected config/cache/stage helpers.

## Control Flow

This header establishes the default implementation flow: `XrdOssSys` creates `XrdOssDir`/`XrdOssFile`; those objects delegate path policy, mapping, cache, and stage decisions back to global `XrdOssSS`; and config parser helpers fill `XrdOssSys` state before service starts.

## State and Persistence Behavior

The header declares extensive process-lifetime configuration: local/remote roots, stage commands, RSS commands, FD fences, trace flags, path/space lists, N2N/stat plugins, preread settings, cache allocation parameters, usage/quota paths, and stage counters. Per-file and per-directory objects own live handles and transient operation state. Durable persistence occurs through the filesystem, cache files, stage/MSS commands, and optional usage/quota files configured elsewhere.

## Dependencies and Integration Points

It includes the public OSS API, config/error/stat headers, OUC export/path-list/stream helpers, and Sys error/pthread headers. It forward-declares cache, stage, name mapping, program, and plugin structures. It is consumed by most `XrdOss*.cc` implementation units.

## Risks and Edge Cases

This is an implementation ABI inside the server. Many public data members are shared across compilation units, so renaming or changing semantics has broad blast radius. `Features()` reports `XRDOSS_HASNAIO|XRDOSS_HASFICL`, with the comment noting async I/O is off for disk and clone-aware behavior; callers must interpret those bits consistently.

## Test Signals

Compile integration across all `XrdOss` sources is essential. Runtime tests should cover configuration permutations, stage/cache/MSS paths, path option macros `Check_RO`/`Check_RW`, AIO feature reporting, and constructor defaults.
