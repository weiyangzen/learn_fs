# File Research: sources/local-fs/xfsdump/restore/bag.h

Declares the intrusive bag abstraction used by restore code.

Key types:
- `bagelem_t`: embedded element owned by a bag while loaded.
- `bag_t`: collection head.
- `bagiter_t`: iterator state with bag, last element, and next element.

API:
- `bag_alloc`
- `bag_insert`
- `bag_remove`
- `bag_find`
- `bagiter_init`
- `bagiter_next`
- `bag_free`

Contract:
- Users embed `bagelem_t` into their own objects.
- Users should not inspect or mutate `bagelem_t` internals directly.
- Payload lifetime remains caller-owned.
