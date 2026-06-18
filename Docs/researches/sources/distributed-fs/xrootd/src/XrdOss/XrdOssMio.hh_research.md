# sources/distributed-fs/xrootd/src/XrdOss/XrdOssMio.hh

## Purpose
Declares the static mmap manager used by OSS to enable, cache, and reclaim memory-mapped file views.

## Important APIs, types, and functions
Defines option bits `OSSMIO_MLOK`, `OSSMIO_MMAP`, and `OSSMIO_MPRM`. Public methods are `Display()`, `isAuto()`, `isOn()`, `Map()`, `preLoad()`, `Recycle()`, and `Set()` overloads. Private methods reclaim mappings by byte amount or object pointer. Static members store the hash table, mutex, permanent queue, idle queue, mode flags, page sizing, max mapping budget, and current in-use byte count.

## Control flow
The header exposes a static lifecycle: config uses `Set()`, open paths use `Map()`, read paths export memory through `XrdOssMioFile`, and close paths call `Recycle()`. Reclaim is internal to `Map()` and reuse handling.

## State and persistence
All declared members are process-static and volatile. No persistent storage is represented.

## Dependencies and integration points
Includes `XrdOssMioFile.hh`, `XrdOucHash`, `XrdSysPthread`, and `XrdSysError`. Used by config parsing/display and file I/O paths that want mmap acceleration.

## Risks and test signals
Because the class is entirely static, tests should isolate state between cases or reset via `Set()` and controlled recycle/reclaim. Callers must honor the `Recycle()` contract to prevent retained mappings and budget exhaustion.
