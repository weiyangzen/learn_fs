# sources/sync-backup/rsync/lib/pool_alloc.h

Purpose: public interface and flags for rsync's pool allocator.

Important APIs/types/functions: flags `POOL_CLEAR`, `POOL_NO_QALIGN`, `POOL_INTERN`, and `POOL_PREPEND`; opaque `alloc_pool_t`; functions `pool_create`, `pool_destroy`, `pool_alloc`, `pool_free`, `pool_free_old`, `pool_boundary`; convenience macros `pool_talloc` and `pool_tfree`.

Control flow: no implementation logic in the header beyond typed allocation/free macros that multiply element size by count before delegating to the pool implementation.

State and persistence behavior: no header state. The opaque handle points to heap state managed by `pool_alloc.c`.

Dependencies/integration: includes `<stddef.h>` for `size_t`; used by file-list and other allocation-heavy rsync modules.

Risks/test signals: macro multiplication can overflow before `pool_alloc` sees the size, so callers must bound counts. API users must honor the documented lifetime rules, especially not mixing `pool_free` and `pool_free_old`.
