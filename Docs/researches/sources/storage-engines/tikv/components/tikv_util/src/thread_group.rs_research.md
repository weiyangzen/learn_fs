# sources/storage-engines/tikv/components/tikv_util/src/thread_group.rs

Purpose: provides process-local thread group properties, currently a shared shutdown flag propagated through thread-local storage.

Important APIs/types/functions: `GroupProperties`, `current_properties`, `set_properties`, `is_shutdown`, and `mark_shutdown`. `GroupProperties` wraps an `Arc<GroupPropertiesInner>` so cloned handles share the same `AtomicBool`.

Control flow: parent code captures `current_properties()` before spawning a thread and the child calls `set_properties`. `mark_shutdown` flips the shared flag; `is_shutdown(true)` panics through `safe_panic!` if no properties were installed.

State and persistence: all state is in-memory TLS plus an `Arc` atomic; nothing is persisted.

Dependencies/integration: used by timer, worker, and YATP pool thread startup paths to propagate shutdown awareness into spawned runtime threads.

Risks: missing `set_properties` silently returns false unless `ensure_set` is true; `SeqCst` is conservative but low-risk.

Test signals: no local tests in this file; coverage is indirect through spawned-thread utilities.
