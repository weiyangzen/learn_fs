## sources/test-tools/filebench/filebench.h

### Purpose
`filebench.h` is the umbrella header for the Filebench runtime. It normalizes platform differences, defines shared scalar types and constants, declares core globals and logging/shutdown functions, and includes most subsystem headers.

### Important APIs, Types, And Functions
Important types and constants include `fbint_t`, `boolean_t`, `u_longlong_t`, `uint_t`, compatibility aliases for 64-bit file APIs, `KB`/`MB`/`GB`, `MMAP_SIZE`, `FILEBENCH_VERSION`, prompt and line limits, shutdown wait seconds, and status codes `FILEBENCH_DONE`, `FILEBENCH_OK`, `FILEBENCH_ERROR`, and `FILEBENCH_NORSC`. It declares `my_pid`, `my_procflow`, `execname`, `filebench_log`, `filebench_shutdown`, and `filebench_plugin_funcvecinit`. It maps `fb_random` to `fb_random64` or `fb_random32` based on word size.

### Control Flow
The header itself drives compile-time control flow through feature macros from `config.h`. It maps missing `off64_t`, `stat64`, `open64`, `pread64`, AIO, mmap, and related symbols to portable equivalents. It also supplies a fallback `sigignore` implementation where needed.

### State And Persistence
It declares process-global runtime state but does not define it. By including many subsystem headers, it establishes a shared-memory-heavy runtime model centered around `filebench_shm` from included IPC definitions.

### Dependencies And Integration Points
Nearly every Filebench C file includes this header directly or indirectly. It pulls in system headers, then Filebench subsystems such as flags, vars, custom variables, AVL, stats, procflow, misc, filesystem plugin, filesets, threadflow, flowops, random, and IPC.

### Risks
As an umbrella header, it creates heavy coupling and potential include cycles. Compatibility macros can hide platform behavior differences, especially around 64-bit file APIs and AIO. Declaring `extern int errno` is obsolete on many modern platforms where `errno` is thread-local macro-backed. The `fb_random` macro changes behavior by architecture.

### Test Signals
Build matrix coverage across Linux, FreeBSD, Solaris-like configurations, AIO/no-AIO, and 32-bit/64-bit is the main signal. Unit tests should verify status-code assumptions and random macro selection in dependent modules.
