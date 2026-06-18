# sources/distributed-fs/xrootd/src/XrdEc/XrdEcWrtBuff.hh

## Purpose

This header defines the write-buffer layer for XrdEc. `BufferPool` limits and recycles large XrdCl buffers, while `WrtBuff` accumulates one erasure-coded data block, splits it into stripes, computes parity, and starts CRC32C futures for each stripe.

## Important APIs, Types, and Functions

`BufferPool::Instance()`, `Create(const ObjCfg&)`, and `Recycle(Buffer&&)` manage up to 1024 reusable `XrdCl::Buffer` objects sized from `objcfg.blksize`.

`WrtBuff` exposes `Write()`, `Pad()`, `GetStrpBuff()`, `GetStrpSize()`, `GetBlkSize()`, `Complete()`, `Empty()`, `Encode()`, and `GetCrc32c()`. It stores `ObjCfg`, an `XrdCl::Buffer`, stripe descriptors, and CRC futures.

## Control Flow

Construction obtains a buffer from the singleton pool, reserves stripe capacity, and zeroes the whole buffer. `Write()` copies user data until `objcfg.datasize` is reached. `Pad()` advances over zero-filled bytes, allocating and clearing if needed. `Complete()` reports whether the data area is full.

`Encode()` creates one stripe descriptor per chunk, marks data stripes valid, invokes the configured redundancy implementation to compute parity, and schedules one digest job per stripe through `ThreadPool`. `GetCrc32c()` blocks on the corresponding future.

Destruction recycles the buffer back into the pool.

## State and Persistence Behavior

State is in-memory and block-local. The write cursor determines block size and stripe sizes. The underlying buffer contains data and parity bytes after `Encode()`. No persistent writes happen here; persistence is handled by `StrmWriter`.

## Dependencies and Integration Points

The file depends on `ObjCfg`, `Config`, `ThreadPool`, XrdCl buffers, and `XrdOucCRC32C`. It integrates with `StrmWriter` for buffering and with XrdEc redundancy plugins for parity calculation.

## Risks and Edge Cases

`BufferPool::Create()` ignores the requested `ObjCfg` when reusing a buffer, so mixed object configurations with different block sizes can be unsafe unless all users share sizing. `Pad()` only clears bytes at construction or allocation time and assumes recycled buffers were reset enough. CRC futures are consumed exactly once; repeated `GetCrc32c()` calls on the same stripe would be invalid.

## Test Signals

Tests should verify boundary writes, partial final blocks, stripe-size calculation, parity invocation for data and parity stripes, CRC scheduling, buffer-pool blocking/recycling, mixed-configuration behavior, and destructor recycling under move construction.
