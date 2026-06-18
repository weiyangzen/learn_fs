# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiShMam.hh

## Purpose
`XrdSsiShMam.hh` declares `XrdSsiShMam`, the default mmap-backed shared-memory table implementation behind the abstract `XrdSsiShMat` interface.

## Important APIs and Types
It implements all `XrdSsiShMat` virtual methods: add, attach, create, export, delete, detach, enumerate, get, info, resize, and sync. Private `MemItem` stores a hash and atomic next offset. `LockType` distinguishes read-only and read-write locks. `XLockHelper` combines process/thread locking and deferred flush behavior.

## Control Flow
Public calls acquire a reader or writer helper, possibly remap if a newer file version is visible, optionally take a file lock, then perform hash-table operations. Destruction detaches the mapping and destroys pthread locks.

## State and Persistence
The header exposes the runtime fields used to represent the mapped file, layout sizes, locking policy, sync policy, access mode, and reuse/multiple-writer behavior. The persistent layout itself is defined privately in the `.cc` file.

## Dependencies and Integration Points
It depends on pthread locks, SSI atomics, and `XrdSsiShMat`. It is instantiated through `XrdSsiShMat::New` and used by `XrdSsi::ShMap<T>`.

## Risks and Test Signals
Tests should verify lock helper cleanup on errors, destructor safety after partial create/attach failure, RO versus RW access checks, and ABI stability for fields hidden behind the abstract interface.
