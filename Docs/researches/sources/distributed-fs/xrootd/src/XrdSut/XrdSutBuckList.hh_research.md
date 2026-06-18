# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.hh

## Purpose

This header declares the lightweight linked-list container used to hold `XrdSutBucket` pointers in exchanged security buffers.

## Important APIs, types, and functions

`XrdSutBuckListNode` stores one bucket pointer and next node. `XrdSutBuckList` exposes `Size`, `End`, `PutInFront`, `PushBack`, `Remove`, `Begin`, and `Next`. The private `Find` helper is implemented in the source file.

## Control flow

The public API supports simple list mutation and single active iteration cursor. It is not a standard STL iterator and cannot support nested iteration on the same list.

## State and persistence behavior

The class stores only pointers and size; no persistence. The list owns nodes but not buckets.

## Dependencies and integration points

It includes `XrdSutBucket.hh` and is included by `XrdSutBuffer.hh`. It exists to avoid heavier container dependencies in old XrdSut code.

## Risks and edge cases

`End()` assumes the list is non-empty. The iterator state is mutable global state within the list object, so concurrent or nested scans will interfere. Callers must explicitly delete buckets if they own them.

## Test signals

Header-level tests are compile/ABI tests plus behavior covered by `XrdSutBuckList.cc` and `XrdSutBuffer` list use.
