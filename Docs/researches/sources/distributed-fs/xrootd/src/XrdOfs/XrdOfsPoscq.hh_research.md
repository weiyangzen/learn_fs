# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPoscq.hh

## Purpose

This header declares `XrdOfsPoscq`, the persistent create queue for POSC cleanup/recovery.

## Important APIs, types, and functions

`Request` is the on-disk fixed-size record containing add time, logical filename, user trace identifier, and reserved bytes. `ReqOffs` and `ReqSize` define file layout. `recEnt` is the in-memory linked-list record returned by initialization/listing, with record offset, mode, and request data.

Public methods are `Add()`, `Commit()`, `Del()`, `Init()`, static `List()`, `Num()`, and the constructor. Private helpers handle initialization failure logging, writing, rewriting, and offset verification.

## Control flow

OFS creates a queue object, calls `Init()` at startup, then uses `Add()` when a POSC create begins, `Commit()` when creation succeeds, and `Del()` when cleanup or recovery removes a pending entry.

## State and persistence behavior

The class owns a durable queue filename and FD plus in-memory maps/free-slot lists. The queue file stores durable recovery intent; `pqMap` and slot lists are rebuilt or updated at runtime.

## Dependencies and integration points

It depends on `XrdOss` for file state and unlink operations, `XrdSysError` for logging, pthread mutexes, and standard map/string. It links POSC offsets to `XrdOfsHandle` and startup recovery logic.

## Risks and test signals

The record layout uses fixed 1024-byte LFN and 288-byte user buffers, so tests should cover truncation and null termination. Offset verification is minimal. Version/sync fields (`pocSV`, `pocWS`) should be covered by tests for configured sync frequency and edge values.
