# File Research: sources/os/linux/linux/block/bio.c

## Scope

This file implements core Linux `struct bio` lifecycle and data-vector helpers: bio/bvec allocation, cloning, chaining, splitting, trimming, iterator-to-bio page extraction, bounce buffering, synchronous waits, completion, page dirtying, and global bioset initialization.

## Core APIs and Entry Points

- Bio initialization/reuse:
  - `bio_init()`, `bio_reset()`, `bio_reuse()`, `bio_uninit()`.
- Allocation and release:
  - `bio_alloc_bioset()`, `bio_kmalloc()`, `bio_put()`, internal `bio_free()`.
  - `bioset_init()`, `bioset_exit()`, `biovec_init_pool()`.
- Chaining and synchronous submission helpers:
  - `bio_chain()`, `bio_chain_and_submit()`, `blk_next_bio()`.
  - `bio_await()`, `submit_bio_wait()`, `bio_submit_or_kill()`, `bdev_rw_virt()`.
- Payload construction:
  - `bio_add_page()`, `__bio_add_page()`, `bio_add_folio()`, `bio_add_folio_nofail()`.
  - `bio_add_virt_nofail()`, `bio_add_vmalloc_chunk()`, `bio_add_vmalloc()`.
  - `bio_iov_iter_get_pages()`, `bio_iov_iter_bounce()`, `bio_iov_iter_unbounce()`.
- Data movement and completion:
  - `__bio_advance()`, `bio_copy_data_iter()`, `bio_copy_data()`, `bio_free_pages()`.
  - `bio_set_pages_dirty()`, `bio_check_pages_dirty()`, `bio_endio()`.
  - `bio_split()`, `bio_trim()`, `guard_bio_eod()`.

## Major State

- `fs_bio_set` is the default global bio pool for general block I/O.
- `bvec_slabs[]` maps requested vector counts to shared `bio_vec` slab caches.
- `bio_slabs` xarray and `bio_slab_lock` share `bio` slabs keyed by combined front pad, `struct bio`, and back pad size.
- `struct bio_alloc_cache` provides per-cpu cached inline-vector bios plus a hardirq side list.
- Biosets may own:
  - `bio_pool` and `bvec_pool` mempools,
  - optional rescuer workqueue/list for avoiding nested allocation deadlocks,
  - optional per-cpu allocation cache.
- Dirty-page deferral uses `bio_dirty_list`, `bio_dirty_lock`, and `bio_dirty_work`.

## Control Flow

- `bio_alloc_bioset()` first tries a non-blocking slab or per-cpu cache allocation. If direct reclaim is allowed and the fast path fails, it punts same-bioset bios from `current->bio_list` to the bioset rescuer and falls back to mempools.
- Inline-vector bios use storage after `struct bio`; larger vector arrays come from `bvec_slabs[]` or the bioset bvec mempool.
- `bio_put()` decrements `__bi_cnt` only when `BIO_REFFED` is set, then either returns an inline-vector bio to the per-cpu cache or fully frees it.
- `bio_chain()` increments the parent remaining count and uses a sentinel `bio_chain_endio`; `bio_endio()` handles chained bios iteratively to avoid recursion.
- `bio_iov_iter_get_pages()` either aliases an existing bvec iterator as a cloned bio or extracts/pins pages into the bio, then aligns total length down if required.
- Bounce-buffer helpers allocate folios, copy write data into them, or store read bounce storage at `bi_io_vec[0]`; unbounce copies read data back and releases pins/folios.
- Direct-I/O read dirtying is deferred if pages became clean before completion, because marking dirty may need process context.
- `init_bio()` creates biovec slabs, registers CPU hotplug cleanup, and initializes `fs_bio_set`.

## Dependencies

- Block APIs: `submit_bio()`, `submit_bio_noacct()`, `bio_advance_iter()`, `bio_integrity_*`, `bio_crypt_*`, `bio_associate_blkg()`, `rq_qos_done_bio()`, zone completion helpers.
- Memory APIs: mempools, slab caches, folios, page pin/unpin, vmalloc mapping helpers, kmap-local bvec access, kmemleak.
- Concurrency: per-cpu caches, CPU hotplug callbacks, spinlocks, atomics, workqueues.

## Risks and Invariants

- Bios allocated with `bio_init()` outside a bioset must be paired with `bio_uninit()` by the owner.
- Callers must not allocate multiple bios from the same mempool under recursive `submit_bio_noacct()` unless previous bios are submitted or a rescuer is available.
- `bio_reuse()` refuses cloned, integrity, and crypto-context bios.
- Bio vector tables are intentionally immutable in several truncation/split paths; callers must use iterators rather than modifying bvec layout.
- `bio_split()` forbids zone append and atomic writes.
- Per-cpu cached bios are `SLAB_TYPESAFE_BY_RCU`, so poll paths must tolerate seeing freshly reallocated bios.
