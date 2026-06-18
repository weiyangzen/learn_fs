# sources/storage-engines/rocksdb/port/win/win_thread.h

Purpose: declares `WindowsThread`, a `std::thread`-like wrapper for Windows builds lacking suitable POSIX-thread-backed `std::thread`.

Important APIs/types/functions: templated constructor, move operations, `joinable`, `get_id`, `native_handle`, `hardware_concurrency`, `join`, `detach`, and `swap`.

Control flow: the templated constructor binds arguments and calls the hidden `Init`; all native implementation details are behind `Data`.

State and persistence behavior: stores shared implementation data and thread id; no persistence.

Dependencies and integration points: included by `port_win.h`; `std::swap` overload is supplied for compatibility with generic thread code.

Risks and test signals: template SFINAE must avoid stealing copy/move construction. Build tests and thread lifecycle tests are useful.
