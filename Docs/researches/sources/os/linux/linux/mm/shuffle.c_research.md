# File Research: sources/os/linux/linux/mm/shuffle.c

Implements optional page allocator freelist shuffling for `CONFIG_SHUFFLE_PAGE_ALLOCATOR`. It randomizes high-order buddy free-list order during memory initialization/hotplug and provides a random head/tail choice helper for allocator insertion.

Key responsibilities:
- Defines the `page_alloc_shuffle_key` static branch and the `shuffle=` module parameter/boot parameter hook.
- Enables shuffling when the boolean parameter is set.
- Validates candidate pages for shuffling: online, same zone, currently buddy-free, and matching buddy order.
- Implements `__shuffle_zone()` as a Fisher-Yates-style random swap pass over order-`SHUFFLE_ORDER` PFN-aligned blocks in a zone.
- Swaps two free-list entries only when they share the same order and pageblock migratetype.
- Implements `__shuffle_free_memory()` to shuffle every zone in a pgdat.
- Implements `shuffle_pick_tail()` to return pseudo-random booleans used by allocator code to vary freelist insertion side.

Important behavior:
- Shuffling operates under the zone lock because it directly swaps `page->lru` entries on buddy free lists.
- Random targets are retried up to `SHUFFLE_RETRY` times to skip holes or unsuitable pages.
- The algorithm explicitly accepts distribution bias; its goal is to reduce allocator predictability rather than provide a mathematically perfect shuffle.
- The zone lock is periodically dropped every 100 order-sized blocks to reduce long lock hold times during large zone initialization.
- `shuffle_pick_tail()` intentionally has unsynchronized static random state; racing updates are considered harmless and add variation.

Dependencies:
- Uses page allocator zone/free-area state, buddy page metadata, pageblock migratetypes, random number helpers, static keys, and kernel parameter infrastructure.

Notable risks:
- The code manipulates allocator free lists directly, so page validation must reject any page not currently on the expected buddy list.
- It assumes same migratetype before `list_swap()`; mixing migration lists would corrupt allocator policy.
- The lock-dropping/rescheduling in `__shuffle_zone()` is necessary for latency but means zone free-list state can change between chunks.
