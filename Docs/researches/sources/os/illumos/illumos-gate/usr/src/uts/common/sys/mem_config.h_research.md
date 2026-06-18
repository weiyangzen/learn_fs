# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mem_config.h

Purpose: Declares kernel physical memory add/delete interfaces, query/status structures, error codes, callback registration, and architecture hooks.

Key structures:
- `memquery_t`: physical, managed, nonrelocatable page counts and nonrelocatable PFN range.
- `memdelstat_t`: physical, managed, and collected page counts during delete.
- `kphysm_setup_vector_t`: post-add, pre-delete, and post-delete callbacks.

Key APIs:
- Add: `kphysm_add_memory_dynamic()`.
- Delete handle lifecycle: `kphysm_del_gethandle()`, `kphysm_del_release()`, `kphysm_del_cancel()`.
- Delete span and query: `kphysm_del_span()`, `kphysm_del_span_query()`.
- Delete execution/status: `kphysm_del_start()`, `kphysm_del_status()`.
- Callback register/unregister.
- Architecture lower interfaces: span check, relocate, support query, PFN deletion query.

Important detail: Error codes model sequencing, nonrelocatable memory, resource shortage, viability failure, cancellation, duplicate spans, and async completion states.

Relevance to subset A: Physical memory hotplug/remove infrastructure.
