# sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_acq_rel_barriers.h

Purpose: implements the playground API using GCC `__atomic` relaxed accesses plus acquire/release fences.

Important APIs and control flow: defines plain `uint64_t` storage, stores with `__atomic_thread_fence(__ATOMIC_RELEASE)` followed by `__atomic_store_n(..., __ATOMIC_RELAXED)`, and loads with relaxed `__atomic_load_n()` followed by `__atomic_thread_fence(__ATOMIC_ACQUIRE)`. `get_mode()` labels the implementation.

State and persistence behavior: in-memory counter synchronization only.

Dependencies and integration points: compiled under `_GCC_ACQ_REL_BARRIERS`; requires GCC/Clang support for `__atomic` builtins.

Risks: TSAN commonly warns that fences are not supported or are not sufficient for race modeling, hence the CMake target suppresses `-Werror=tsan`. This variant is diagnostic, not a recommended pattern without verifying sanitizer behavior.

Test signals: `collect_warnings.sh` should show whether TSAN reports races or unsupported-fence summaries for this executable.
