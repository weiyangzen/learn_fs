# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.hh

## Purpose

This header declares the C ABI for XrdFfs directory-entry list and cache helpers. It is intentionally C-compatible so both C-style FUSE code and C++ XrdPosix wrappers can share directory merge logic.

## Important APIs, Types, and Functions

`struct XrdFfsDentnames` is a singly linked node containing a heap-owned name and next pointer. Public functions add, delete, join, and extract names from these lists. Cache functions initialize, fill, search, and destroy the global directory-entry cache.

## Control Flow

Callers build one or more `XrdFfsDentnames` lists with `names_add()`, optionally join them, then call `names_extract()` to obtain a sorted array. Directory listing code can then call `cache_fill()` with that array, and later stat paths can call `cache_search()` with a directory and child name.

## State and Persistence Behavior

The header declares interfaces for process-global cache state implemented in the source file. There is no durable persistence; callers own arrays returned by `names_extract()` and must free each string and the array.

## Dependencies and Integration Points

The header includes C library string/allocation/time headers and pthreads. It is consumed by `XrdFfsPosix.cc`, `XrdFfsMisc.cc`, and the XrdFfs build target.

## Risks and Edge Cases

There are no include guards in this header, so repeated inclusion depends on build behavior and may cause redeclaration problems in stricter contexts. The ABI uses raw `char*` and double pointers, making ownership conventions critical.

## Test Signals

Compile tests should include the header from C and C++ translation units. Runtime tests should pair it with the implementation's list ownership and cache lifecycle tests.
