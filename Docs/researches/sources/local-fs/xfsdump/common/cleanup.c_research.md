# File Research: sources/local-fs/xfsdump/common/cleanup.c

Purpose: provides a small cleanup callback registry invoked during program shutdown.

Key behavior:
- Stores callbacks in a singly linked LIFO list of `struct cu`.
- `cleanup_init` clears the root list.
- `cleanup_register` registers a normal cleanup callback.
- `cleanup_register_early` registers a callback with `CU_EARLY`, intended to run before kill-all style shutdown.
- `cleanup_cancel` removes a registered callback and frees its node.
- `cleanup` invokes and frees all callbacks in LIFO order.
- `cleanup_early` walks the list, invokes only `CU_EARLY` callbacks, removes them, and leaves normal callbacks registered.

Important details:
- `cleanup_t` is an opaque `void` typedef in the header, with implementation nodes cast to/from `cleanup_t *`.
- Allocation uses `calloc` and `assert`, so allocation failure aborts in assertion-enabled builds.
- There is no locking; expected use is single-threaded or externally serialized.

Risks/notes:
- Callback execution order is reverse registration order.
- `cleanup_cancel` asserts the target exists; passing an already-run or invalid handle is fatal in debug/assert builds.
