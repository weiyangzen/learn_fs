# sources/storage-engines/rocksdb/util/channel.h

Purpose: implements a simple blocking FIFO channel template for moving `T` values between producer and consumer threads, with explicit EOF signaling.

Important APIs and types: `channel<T>` owns a `std::queue<T>`, `std::mutex`, `std::condition_variable`, and `eof_` flag. `write(T&&)` pushes an element and wakes one waiter. `read(T&)` blocks until EOF or data, moves the front value into the output parameter, pops it, and returns false only when EOF is reached and the queue is empty. `sendEof()` sets EOF and wakes all waiters. `eof()` reports true only when the buffer is empty and EOF was sent. `size()` returns the buffered count.

Control flow and state: all public state access locks `lock_`. Reads drain queued data even after EOF is signaled, then return false once empty. The second `notify_one` in `read` can wake another waiter after a pop, though there is no bounded capacity in this implementation.

Dependencies and integration: depends only on standard condition-variable, mutex, queue, and utility headers plus RocksDB namespace. It is a generic utility; no direct integration from the required subset was needed for interpretation.

Risks and test signals: `write` after `sendEof` is not rejected, so caller protocol must prevent post-EOF writes or consumers can observe surprising behavior. The channel is unbounded and can grow under producer pressure. `write` only accepts rvalues. No direct tests appear in this subset.
