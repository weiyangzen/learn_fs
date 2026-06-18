# sources/storage-engines/sqlite/src/vxworks.h research

## Purpose
`vxworks.h` centralizes compile-time platform detection and feature macros for Wind River VxWorks builds of SQLite.

## Important APIs, types, and functions
The header declares no functions or types. On `__RTP__` or `_WRS_KERNEL` it includes VxWorks and pthread headers and defines `OS_VXWORKS`, `SQLITE_OS_OTHER`, `SQLITE_HOMEGROWN_RECURSIVE_MUTEX`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_ENABLE_LOCKING_STYLE`, and `HAVE_UTIME`. Otherwise it sets `OS_VXWORKS` to zero if needed and defines `HAVE_FCHOWN`, `HAVE_READLINK`, and `HAVE_LSTAT`.

## Control flow
All behavior is preprocessor selection between the VxWorks branch and the non-VxWorks fallback branch.

## State and persistence behavior
No runtime state exists. The file affects compilation of OS, mutex, extension-loading, and file-feature paths elsewhere.

## Dependencies and integration points
On VxWorks it depends on `<vxWorks.h>` and `<pthread.h>`. Its macros are consumed by SQLite's OS abstraction and build configuration.

## Risks and test signals
Incorrect detection can select wrong mutex/filesystem behavior. VxWorks builds omit loadable extensions and disable locking-style support. Build tests should compile VxWorks RTP, VxWorks kernel, and non-VxWorks variants and verify macro-driven OS-layer behavior.
