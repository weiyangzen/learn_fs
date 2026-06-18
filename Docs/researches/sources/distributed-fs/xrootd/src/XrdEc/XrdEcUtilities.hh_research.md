# sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.hh

## Purpose

This header provides shared utility types for XrdEc: stripe descriptors, byte buffers, an exception wrapper for XrdCl status, asynchronous callback scheduling declarations, a blocking interruptible queue, and a filename-to-block helper.

## Important APIs, Types, and Functions

`stripe_t` pairs a stripe buffer pointer with a validity flag, and `stripes_t` is the vector passed to redundancy-code implementations. `buffer_t` aliases `std::vector<char>`.

`IOError` wraps an `XrdCl::XRootDStatus`, exposes `what()` as `ToString()`, and returns the original status through `Status()`. It defines `ioTooManyErrors` as a local error discriminator.

`sync_queue<Element>` provides `enqueue()`, blocking `dequeue()`, nonblocking `dequeue(Element&)`, `empty()`, and `interrupt()`. Blocking dequeue throws `wait_interrupted` after the queue is awakened with the interrupt flag set.

`fntoblk()` parses a block number from the substring between the last two dots of a filename.

## Control Flow

`sync_queue::dequeue()` waits on a condition variable while the queue is empty. `interrupt()` sets an atomic flag and notifies all waiters. Producers move elements into an STL queue and notify waiters; consumers move the front element out.

## State and Persistence Behavior

All state is in memory. `sync_queue` owns queued elements and an interrupt flag. `IOError` copies the status and string message so the exception remains valid after the original status object goes out of scope.

## Dependencies and Integration Points

The header depends on XrdEc object configuration and several XrdCl headers. `sync_queue` is used directly by `StrmWriter` to coordinate futures between user/write threads and the writer thread. `stripe_t` feeds the redundancy plugins configured by `Config::GetRedundancy()`.

## Risks and Edge Cases

`sync_queue::dequeue()` checks `interrupted` only after a condition-variable wake inside the empty loop; if `interrupt()` happens before a thread enters `wait()`, a later blocking `dequeue()` on an empty queue can still wait until another notify. `fntoblk()` assumes the filename contains at least two dots and a numeric middle suffix; malformed names throw from `std::stoul`.

## Test Signals

Useful tests cover FIFO behavior, moving futures or move-only elements, interruption before and during waits, nonblocking empty dequeue, exception message stability, and block-number parsing for normal and malformed XrdEc chunk names.
