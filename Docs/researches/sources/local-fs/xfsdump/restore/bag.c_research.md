# File Research: sources/local-fs/xfsdump/restore/bag.c

Implements a small intrusive “bag” collection abstraction for restore code.

Data structure:
- Circular doubly linked list.
- Caller embeds `bagelem_t` inside payload objects.
- Each element stores loaded flag, owning bag, search key, payload pointer, and links.

Functions:
- `bag_alloc()` allocates and zeroes a bag.
- `bag_insert()` inserts a caller-provided element at the head, records key and payload.
- `bag_remove()` removes an element, returns its key/payload, and zeroes the embedded element.
- `bag_find()` linearly searches by key and returns the matching embedded element plus payload.
- `bagiter_init()` initializes a stable iterator over current bag contents.
- `bagiter_next()` returns next element and payload; callers may remove returned elements before continuing.
- `bag_free()` zeroes all embedded elements and frees the bag object.

Complexity:
- Insert/remove are O(1).
- Find and iteration are O(n).

Assumptions:
- Assertions enforce correct ownership/loading in debug-enabled builds.
- Not thread-safe.
- `bag_free()` clears embedded elements but does not free caller-owned payload objects.
