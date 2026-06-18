# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepare.hh

## Purpose

This header defines the OFS prepare plugin interface. Prepare plugins customize `kXR_prepare` behavior for staging, prefetching, eviction, cancellation, and query workflows.

## Important APIs, types, and functions

`XrdOfsPrepare` is an abstract base class with pure virtual `begin()`, `cancel()`, and `query()` methods. `XrdOfsgetPrepare_t` is the factory signature for creating a prepare plugin from a shared library. `XrdOfsAddPrepare_t` is the wrapper factory signature for stacking a new prepare plugin around an existing one. Macros define the canonical argument lists for exported functions.

## Control flow

`XrdOfsConfigPI` loads a library, resolves `XrdOfsgetPrepare`, passes logger/config/parameters/SFS/OSS/environment pointers, and stores the returned object. Additional `++` prepare plugins are loaded through `XrdOfsAddPrepare`, receiving the current plugin pointer for wrapping.

## State and persistence behavior

The interface owns no state. Implementations decide whether prepare request IDs and staging state are durable or in-memory.

## Dependencies and integration points

The header forward-declares OSS, environment, error info, security identity, SFS filesystem, and `XrdSfsPrep`. It is consumed by OFS request handling, plugin config, and concrete prepare plugins such as `XrdOfsPrepGPI.cc`.

## Risks and test signals

Return-code semantics are part of the contract: `SFS_DATA` and `SFS_OK` carry request IDs differently for `begin()`, while cancel/query have narrower return sets. Plugin tests should validate exported symbol names, null factory failure, stacked wrapper behavior, and how OFS translates `SFS_STARTED`, `SFS_DATA`, and `SFS_ERROR` responses.
