# sources/storage-engines/rocksdb/port/win/win_thread.cc

Purpose: implements a Windows thread wrapper used when MinGW/std::thread support is not POSIX-thread backed.

Important APIs/types/functions: `WindowsThread::Init`, constructor/destructor, move assignment, `joinable`, `native_handle`, `hardware_concurrency`, `join`, `detach`, `swap`, and `Data::ThreadProc`.

Control flow: constructor binds callable arguments into `std::function<void()>`, stores them in shared `Data`, starts a thread with `_beginthreadex`, and transfers a heap-held `shared_ptr` to the thread proc. `join` waits with `WaitForSingleObject`, closes the handle, and rejects self-join. `detach` closes the handle without waiting.

State and persistence behavior: owns shared thread data, a native handle, and thread id. No persistence.

Dependencies and integration points: selected by `port_win.h` as `port::Thread` when `_POSIX_THREADS` is unavailable; used by `WinEnvThreads`.

Risks and test signals: destructor terminates if still joinable, matching `std::thread`; handle closure and detached lifetime rely on shared ownership. Thread, Env scheduling, and MinGW build tests are key.
