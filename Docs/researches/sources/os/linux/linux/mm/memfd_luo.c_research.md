# File Research: sources/os/linux/linux/mm/memfd_luo.c

## Role

Live Update Orchestrator file-preservation handler for memfd files across kexec. It serializes selected memfd state into KHO-preserved memory, preserves the backing folios, freezes mutable shmem state during preparation, restores a new memfd in the next kernel, and cleans up preserved or restored resources depending on the live-update outcome.

## Key Behavior

- Documents the unstable LUO memfd preservation contract: file contents, size, file position, status flags, and known seals are preserved; properties such as `FD_CLOEXEC` are reset; hugetlb-backed memfds are rejected.
- `memfd_luo_preserve_folios()` handles empty files without folio metadata; otherwise it estimates a page-sized upper bound, allocates a folio pointer array, pins all file indices with `memfd_pin_folios()` so pages are resident and immovable, allocates serialized folio records, KHO-preserves each folio, forces every folio dirty, zeroes and marks non-uptodate folios, records PFN/index/flags, and preserves the serialized folio array via KHO vmalloc preservation.
- The preserve path intentionally fills sparse holes by pinning all file offsets; the comments call out possible future performance work to avoid allocating every missing page.
- `memfd_luo_unpreserve_folios()` reverses a prepared-but-not-committed preservation by unpreserving the vmalloc metadata, unpreserving each folio, unpinning it, and freeing the serialized array.
- `memfd_luo_preserve()` locks the inode, freezes shmem, allocates the main serialized structure in preserved memory, validates current seals against `MEMFD_LUO_ALL_SEALS`, records file position, size, and seals, rejects files whose page count exceeds `UINT_MAX`, preserves folios, stores the serialized physical address, and leaves shmem frozen until later unpreserve/finish handling.
- `memfd_luo_freeze()` updates only the saved file position at freeze time because file offset can change after prepare while size/folios/seals are frozen.
- `memfd_luo_unpreserve()` thaws shmem and frees all preserved state if the original-kernel preservation is cancelled.
- `memfd_luo_finish()` runs in the source/old context when retrieval did not happen; it restores preserved metadata enough to drop folio references, discards preserved folios, frees vmalloc metadata, and frees the serialized structure.
- `memfd_luo_retrieve_folios()` restores preserved folios by physical address, locks and marks them swap-backed, charges them to memcg, inserts them into the new shmem page cache, restores uptodate/dirty flags, accounts shmem inode blocks, adds them to LRU, recalculates inode state, and unwinds uninserted folios on error.
- `memfd_luo_retrieve()` validates serialized data and seals, creates a new seal-capable memfd, reapplies seals, restores file position and size, restores folio metadata from KHO vmalloc memory, inserts all folios, returns the new file through `args->file`, and frees the serialized KHO state.
- `memfd_luo_can_preserve()` accepts only anonymous shmem memfds (`shmem_file(file)` with no inode links), which excludes hugetlbfs and linked shmem files.
- Registers a `liveupdate_file_handler` at `late_initcall()` with preserve, freeze, unpreserve, finish, retrieve, can-preserve, and ID callbacks; registration errors other than `-EOPNOTSUPP` are logged and returned.

## Dependencies

Uses the liveupdate file-handler API, KHO preserved allocation/vmalloc/folio helpers, shmem freeze and page-cache insertion helpers, memfd allocation and sealing helpers from `memfd.c`, folio pinning/unpinning, memcg charging, file position helpers, vmalloc, PFN/physical address conversion, and serialized ABI definitions from `linux/kho/abi/memfd.h`.

## Research Notes

The preservation model favors correctness over sparseness and reclaimability: all holes are materialized, all folios are marked dirty, and non-uptodate folios are zeroed before preservation so restored user data cannot be lost under reclaim. The restore path depends on careful resource ownership transfer from KHO-preserved physical folios into a new shmem mapping; failures deliberately leave already inserted folios owned by the new file while dropping only not-yet-inserted restored folios. The handler is intentionally narrow because only anonymous shmem memfds have the expected sealing and page-cache semantics.
