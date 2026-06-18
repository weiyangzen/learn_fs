# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_rlock.c

This file implements ZFS range locking over byte ranges. It exposes `rangelock_init()`, `rangelock_fini()`, `rangelock_enter()`, `rangelock_exit()`, and `rangelock_reduce()`, using an AVL tree ordered by starting offset to coordinate readers, writers, append writes, and temporary whole-file locks used during block-size growth.

Writer and append acquisition is handled by `rangelock_enter_writer()`. A caller-provided callback may rewrite `RL_APPEND` into an `RL_WRITER` at EOF and may enlarge a writer range, commonly to `UINT64_MAX` for whole-file exclusion while growing a file block size. Writers wait on overlapping tree nodes and reset their requested offset, length, and type after each wakeup because the callback may have changed them.

Reader locking supports overlapping shared ranges through proxy locks. `rangelock_proxify()` replaces an original reader lock in the tree with a proxy node; `rangelock_split()` divides a proxy range at an interior offset; `rangelock_new_proxy()` creates proxy segments for gaps. `rangelock_add_reader()` walks overlapping reader ranges, splits them as needed, and increments per-segment reference counts so overlapping reader ranges can be represented as disjoint AVL spans.

`rangelock_enter_reader()` blocks readers behind active writers and behind queued writers on overlapping ranges. This avoids continuous reader arrivals starving a waiting writer. Waiters lazily initialize per-node read and write condition variables and mark `lr_read_wanted` or `lr_write_wanted`.

Unlocking preserves the proxy model. `rangelock_exit_reader()` removes ordinary reader locks directly, but for proxy-backed original handles it finds the start proxy and decrements every contiguous proxy segment covering the original range, freeing zero-count segments and broadcasting waiters. Writer unlocks remove the single writer node, wake waiters, and free the handle.

`rangelock_reduce()` shrinks a whole-file writer lock to a caller-specified subrange after block-size growth has completed. It asserts that the tree contains only the whole-file writer, then updates the range and broadcasts waiters. The main correctness risks in this file are off-by-one overlap checks, proxy split/refcount consistency, waiter CV lifecycle, and the callback contract for append and block-growth conversion.
