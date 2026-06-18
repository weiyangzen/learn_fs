# sources/storage-engines/rocksdb/util/thread_guard.h

## Purpose

Defines an RAII wrapper around `port::Thread` that joins the owned thread during destruction.

## APIs, control flow, and state

`ThreadGuard` default-constructs empty or accepts an rvalue `port::Thread`. Copying is disabled and moving is defaulted. The destructor calls `join()` only if the stored thread is joinable. `GetThread` returns const or mutable references to the owned thread.

## Dependencies and integration

It depends on `port/port.h`. It is useful in tests and utility code where exception-safe or early-return-safe thread joining is needed.

## Risks and test signals

No direct tests are present. The main risk is destruction from the same thread it owns, which would attempt self-join through `port::Thread` behavior. Move assignment relies on `port::Thread` semantics and does not add custom joining of an overwritten joinable thread.
