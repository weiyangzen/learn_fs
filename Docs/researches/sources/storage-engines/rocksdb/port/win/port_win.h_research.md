# sources/storage-engines/rocksdb/port/win/port_win.h

Purpose: Windows port header for RocksDB's synchronization, allocation, path, thread-local, and platform helper APIs.

Important APIs/types/functions: `Mutex`, `RWMutex`, `CondVar`, `Thread` alias, `OnceType`, cache-line allocation helpers, `AsmVolatilePause`, pthread TLS shims, truncate/crash/exit/process/UUID helpers, UTF conversion helpers, and `RX_*` path/function macros.

Control flow: compile-time routing selects `std::thread` or `WindowsThread`, jemalloc or `_aligned_malloc`, UTF-16 Win32 APIs or ANSI APIs, and Windows SRW locks/condition variables.

State and persistence behavior: synchronization objects own mutex/SRW state; TLS keys map to Windows TLS slots; file persistence is delegated to declared truncate and Env/I/O implementations.

Dependencies and integration points: included through `port/port.h` on Windows; consumed across RocksDB core. It includes `win_thread.h`, Windows headers, and RocksDB port definitions.

Risks and test signals: Windows macro collisions are actively undefined; UTF filename mode changes ABI expectations for path strings. Build matrix coverage with MSVC, MinGW, `_POSIX_THREADS`, UTF filenames, and jemalloc is important.
