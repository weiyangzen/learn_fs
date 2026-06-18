# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.cc

## Purpose

This file implements a minimal singly linked list used by `XrdSutBuffer` to manage `XrdSutBucket` pointers without owning the buckets themselves.

## Important APIs, types, and functions

`XrdSutBuckList` implements construction from an optional first bucket, destruction of list nodes, duplicate-checked `PutInFront` and `PushBack`, `Remove`, and pseudo-iterator methods `Begin` and `Next`. The private `Find` helper performs pointer-identity search.

## Control flow

Insertion first searches for the exact bucket pointer and adds a node only if not already present. `Remove` tries to use cached iterator state (`current`/`previous`) when valid, otherwise scans from the beginning. Iteration resets with `Begin`, then advances with `Next`.

## State and persistence behavior

The list stores node pointers, iterator cursor state, end pointer, and size. It does not delete the `XrdSutBucket` objects; `XrdSutBuffer` deletes buckets by iterating the list before the list nodes are destroyed.

## Dependencies and integration points

The file depends only on `XrdSutBuckList.hh` and, through that, `XrdSutBucket`. It is an internal support container for serialized authentication exchange buffers.

## Risks and edge cases

`End()` in the header dereferences `end` without null checking. `Remove` sets `previous = curr` after deleting `curr` in the non-head case, leaving a dangling cached previous pointer until the next iterator reset; current callers usually iterate/delete carefully, but this is fragile. The class is not thread-safe and uses raw pointers throughout. Pointer-identity duplicate detection means two equal bucket values can coexist if they are distinct objects.

## Test signals

Tests should cover empty list behavior, insertion order, duplicate pointer rejection, removal of head/middle/tail/missing buckets, iterator behavior after removal, and ownership interaction with `XrdSutBuffer` destruction.
