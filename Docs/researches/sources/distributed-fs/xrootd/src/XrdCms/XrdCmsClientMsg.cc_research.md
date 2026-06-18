# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClientMsg.cc

## Purpose
Implements a fixed-size table of outstanding CMS client messages, assigning stream IDs, waiting for manager replies, decoding replies, and recycling message slots.

## Important APIs, Types, and Functions
Implements `Alloc()`, `Init()`, `Recycle()`, static `Reply()`, and private `RemFromWaitQ()`. Static state includes `nextid`, `numinQ`, `msgTab`, `nextfree`, and `FreeMsgQ`.

## Control Flow
`Init()` allocates 1024 message objects and links them into the free list. `Alloc()` pops one, assigns a generation-encoded ID, stores the caller's `XrdOucErrInfo`, locks its condition variable, and marks it waiting. `Reply()` removes the matching slot by stream ID, decodes the response through `XrdCmsParser::Decode()`, signals the waiter, and unlocks. `Recycle()` removes a waiter from service and returns it to the free list.

## State and Persistence Behavior
All state is process-local and fixed-size. IDs combine a low-bit table index with generation bits to reject stale replies. No durable persistence.

## Dependencies and Integration Points
Depends on CMS wire headers, parser, trace, Ouc buffers/error info, and pthread condition variables. Used by `XrdCmsClientMan` when sending synchronous manager requests.

## Risks and Edge Cases
At most 1024 concurrent messages can be outstanding. `numinQ` is a static counter guarded only around free-list operations but returned without locking. `Recycle()` substitutes a static dummy response because replies may race with recycling. Stale or unknown replies are logged only at debug level.

## Test Signals
Tests should cover ID generation/wrap, stale reply rejection, table exhaustion, wait/signal behavior, decode result propagation, concurrent allocation/recycle, and in-queue accounting.
