# sources/storage-engines/wiredtiger/tools/tsan_playground/api_gcc_full_barriers.h

Purpose: implements the playground API using GCC sequentially consistent fences around relaxed access.

Important APIs and control flow: `atomic_store_release()` executes `__atomic_thread_fence(__ATOMIC_SEQ_CST)` then relaxed store. `atomic_load_acquire()` performs relaxed load then a seq-cst fence. `get_mode()` labels the variant.

State and persistence behavior: in-memory synchronization wrapper only.

Dependencies and integration points: selected by `_GCC_FULL_BARRIERS`; CMake suppresses TSAN warning-as-error for this target.

Risks: full barriers may not be represented as sanitizer synchronization around relaxed operations. This is a comparison target for TSAN behavior rather than a production abstraction.

Test signals: runtime TSAN summaries from `collect_warnings.sh` indicate whether the sanitizer accepts or flags this style.
