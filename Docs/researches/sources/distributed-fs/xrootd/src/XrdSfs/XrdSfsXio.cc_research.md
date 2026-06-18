# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXio.cc

## Purpose
Implements the static portions of the SFS exchange-buffer I/O interface by forwarding `XrdSfsXio::Buffer()` and `XrdSfsXio::Reclaim()` to a process-global implementation object.

## Important APIs, Types, And Functions
- Anonymous `Impl` stores static `XrdSfsXioImpl *xio`.
- `XrdSfsXio::XrdSfsXio(XrdSfsXioImpl &xioimpl)` initializes the global implementation through a function-local static `Impl`.
- `XrdSfsXio::Buffer()` and `Reclaim()` forward to function pointers in `XrdSfsXioImpl`.

## Control Flow
The first construction of an `XrdSfsXio` object initializes the static `Impl dummy` with the supplied implementation. Subsequent constructions do not replace it. Static calls dereference the stored implementation and invoke the configured buffer/reclaim functions.

## State And Persistence
Maintains one process-global implementation pointer for all exchange-buffer static methods. It does not persist buffer contents; ownership is handled by the implementation.

## Dependencies And Integration Points
Depends on `XrdSfsXio.hh` and `XrdSfsXioImpl.hh`. Integrates with file implementations that opt into exchange-buffer I/O via `XrdSfsFile::setXio()`.

## Risks And Edge Cases
- Static methods crash if called before any `XrdSfsXio` instance initializes `Impl::xio`.
- Only the first implementation wins. Mixed implementations in one process are unsupported.
- Thread-safe initialization relies on C++ function-local static semantics.

## Test Signals
Construct an implementation and verify static forwarding, call ordering before initialization, repeated construction with different implementations, and concurrent first-use behavior.
