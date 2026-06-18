# sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.hh

## Purpose
This header defines the Python `FileSystem` binding type and its method table.

## Important APIs, Types, and Functions
`class FileSystem` declares static filesystem methods and stores `URL *url` plus `XrdCl::FileSystem *filesystem`. The header defines `FileSystemMethods`, `FileSystem_init`, `FileSystem_dealloc`, `FileSystemMembers`, and static `FileSystemType`.

## Control Flow
Construction creates a Python `URL` from the provided args and then constructs an XrdCl filesystem from that URL. Deallocation deletes the XrdCl filesystem and decrefs the URL. Python method dispatch is described by the method table.

## State and Persistence
In-memory object state is the server URL and filesystem client instance. Persistence is through implementation methods in the source file.

## Dependencies and Integration Points
Depends on `PyXRootDURL.hh`, `Conversions.hh`, and `XrdClFileSystem`. Included by module initialization and filesystem implementation.

## Risks and Test Signals
If URL construction fails, initialization returns failure before creating the filesystem. Static type definition in a header requires controlled inclusion. Tests should verify constructor argument validation, `url` member exposure, deallocation, and method availability.
