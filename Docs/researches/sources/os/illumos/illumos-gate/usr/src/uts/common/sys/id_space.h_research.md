# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/id_space.h

This header defines a generic ID space allocator API backed by `vmem_t`.

Key definitions:
- `typedef vmem_t id_space_t;`
- API:
  - `id_space_create(const char *, id_t, id_t)`
  - `id_space_destroy(id_space_t *)`
  - `id_space_extend(id_space_t *, id_t, id_t)`
  - `id_alloc`, `id_alloc_nosleep`
  - `id_allocff`, `id_allocff_nosleep`
  - `id_alloc_specific_nosleep`
  - `id_free`

Dependencies:
- Includes `sys/param.h`, `sys/types.h`, `sys/mutex.h`, and `sys/vmem.h`.

Behavioral notes:
- Provides sleeping and non-sleeping allocation variants.
- Provides first-fit variants and specific-ID allocation.
- Used by subsystems that need bounded ID allocation; `ipc_impl.h` uses it for IPC object IDs.

Relevance:
- Common kernel infrastructure for identifiers, relevant to filesystems and storage control planes where stable object IDs are required.
