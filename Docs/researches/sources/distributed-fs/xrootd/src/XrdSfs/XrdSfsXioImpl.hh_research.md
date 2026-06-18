# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsXioImpl.hh

## Purpose
Defines the private implementation hook used by `XrdSfsXio` static methods.

## Important APIs, Types, And Functions
- `XrdSfsXioImpl::Buffer_t` and `Reclaim_t` are function-pointer types.
- Members `Buffer` and `Reclaim` hold the active implementations.
- Constructor stores the two function pointers.

## Control Flow
An `XrdSfsXio` subclass constructs an `XrdSfsXioImpl` with concrete static functions and passes it to the `XrdSfsXio` base constructor. `XrdSfsXio.cc` then forwards static calls through these pointers.

## State And Persistence
Only stores function pointers. It owns no buffers and has no persistence.

## Dependencies And Integration Points
Includes `XrdSfsXio.hh` for handle types. It is intended as a private interface for exchange-buffer implementations, not as an end-user plugin API.

## Risks And Edge Cases
Null function pointers are not guarded in the constructor or callers. Lifetime must exceed all static forwarding calls because `XrdSfsXio.cc` stores the pointer globally.

## Test Signals
Verify construction with valid functions, static forwarding through `XrdSfsXio`, and failure behavior if a null or short-lived implementation is supplied.
