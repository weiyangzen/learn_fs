# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucTable.hh

Purpose: implements a fixed-capacity templated pointer table with optional string keys and a free-list allocator for numeric slots.

Important APIs, types, and functions: constructor allocates `OucTable` entries and initializes free-list links. Public methods include `Alloc()`, `Insert()`, `Find()`, `Item()`, `Next()`, `Apply()`, `Remove()`, and `Delete()`. Each entry stores either an item key or next-free index in a union.

Control flow: `Alloc()` pops a slot from the free list and extends `curnum`. `Insert()` places an item and duplicated key in a chosen or allocated slot. `Find()` scans live entries for a matching key. `Remove()` frees the key, returns the item without deleting it, pushes the slot onto the free list, and may shrink the current high-water mark. `Delete()` wraps `Remove()` and deletes the returned item.

State and persistence: state is an owned heap array, free-list head, maximum size, and current high-water mark. Items are heap pointers owned by the table until removed. No persistence or locking exists.

Dependencies and integration points: depends on C allocation/string headers and is useful where legacy code needs stable small integer handles for object pointers.

Risks and test signals: `Insert()` calls `strdup(key)` even when `key` is null, which is undefined or crashes on typical libc. The shrink loop in `Remove()` checks `Table[curnum]` after decrement choices and needs boundary coverage. Tests should cover capacity exhaustion, keyed and unkeyed insertion, null keys, removal/deletion ownership, `Next()` iteration, and destructor cleanup.
