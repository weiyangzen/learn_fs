# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.hh

## Purpose
Declares the final `XrdClS3::Filesystem` plugin that exposes S3 buckets/objects through the `XrdCl::FileSystemPlugIn` API.

## Important APIs, Types, and Functions
Overrides `DirList`, `Locate`, `MkDir`, `Query`, `Rm`, `RmDir`, `Stat`, `GetProperty`, and `SetProperty`. Private `GetFSHandle()` returns endpoint-specific wrapped `XrdCl::FileSystem` objects. Nested `S3HeaderCallout` signs HTTP filesystem requests.

## Control Flow
The filesystem instance holds a base S3 URL with path/query stripped. Operations join that base URL with the requested path, translate/sign as needed, and either perform custom S3 logic for directory-like operations or delegate to a cached HTTP filesystem handle.

## State and Persistence Behavior
The class owns in-memory properties, a cache of raw `XrdCl::FileSystem*` handles keyed by endpoint, the base URL, logger, locks, and a header callout. S3-visible persistence is created by implementation methods, not by the declaration itself.

## Dependencies and Integration Points
Includes the HTTP header callout interface and XrdCl plugin interface. Implementation integrates with TinyXML, S3 URL/signing factory helpers, and XRootD HTTP filesystem operations.

## Risks and Edge Cases
The header declares `m_is_opened` though filesystem open state is not used in the implementation. Raw handle ownership in `m_handles` needs destructor cleanup auditing. Property locking is narrow, while lifecycle and handle-cache access use a separate shared mutex.

## Test Signals
ABI compile tests should verify override signatures against XrdCl. Unit tests should cover handle caching, property access, base URL normalization, and callout lifetime.
