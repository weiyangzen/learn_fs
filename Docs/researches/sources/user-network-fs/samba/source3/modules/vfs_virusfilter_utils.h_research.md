# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.h

## Purpose
This header declares the utility API shared by the virusfilter core and scanner backends, including socket I/O handles, result cache types, substitution helpers, cache operations, and shell execution wrappers.

## Important APIs, Types, and Functions
It defines buffer and I/O constants: URL max, line buffer size, EOL size, iovec max, and cache buffer size. `struct virusfilter_io_handle` stores a tstream, connect/I/O timeouts, read/write EOL bytes, and an internal read buffer. `struct virusfilter_cache_entry` stores timestamp, result, and report. `struct virusfilter_cache` stores a memcache handle, talloc context, and time limit. Function declarations cover path substitution, next-module move, line socket connect/read/write variants, cache lifecycle and mutation, and shell environment/command execution.

## Control Flow
The header exposes a layered design: backends use I/O functions to talk to scanner daemons; the core uses cache functions before/after scans and shell helpers when handling infected or error outcomes.

## State and Persistence
The declared structs are in-memory only. The I/O handle can preserve a scanner stream across requests, and the cache stores transient scan decisions. No on-disk format is defined here.

## Dependencies and Integration Points
It includes `vfs_virusfilter_common.h`, Samba memcache, and strv helpers. Any backend including this header receives both the common virusfilter ABI and these utilities.

## Risks
Constants assume PATH_MAX-scaled scanner commands fit in fixed buffers; callers must avoid truncation and overflow. The EOL size is one byte in this header, but the Sophos backend requests a two-byte CRLF read EOL, which the setter rejects because `VIRUSFILTER_IO_EOL_SIZE` is 1. That mismatch can make CRLF protocol handling ineffective.

## Test Signals
Compile-time and runtime tests should validate EOL settings for all backends, maximum path handling, cache entry ownership, and that public declarations match implementation attributes such as printf-style varargs.
