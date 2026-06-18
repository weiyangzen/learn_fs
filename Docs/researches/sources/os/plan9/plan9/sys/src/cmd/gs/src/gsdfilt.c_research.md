# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdfilt.c

## Role

`gsdfilt.c` implements the device filter stack stored in `gs_state`. Device filters wrap the current device with forwarding/filtering devices and can later be popped to restore the previous target.

## Main Functions

- `gs_push_device_filter(...)`
- `gs_pop_device_filter(...)`
- `gs_clear_device_filters(...)`

It also defines GC descriptors for `gs_device_filter_stack_t` and `gs_device_filter_t`.

## Push Flow

`gs_push_device_filter` allocates a stack node, increments the current device reference, saves it as `next_device`, calls the filter’s `push` hook to create a new device, pushes the stack node, installs the new device with `gs_setdevice_no_init`, then drops the temporary new-device reference.

## Pop Flow

`gs_pop_device_filter` rejects empty stacks, removes the top stack node, calls the filter’s `prepop`, switches the graphics state back to the saved next device, decrements stack references, calls `postpop`, and drops the old top device reference.

`gs_clear_device_filters` repeatedly pops until empty.

## Dependencies

Uses graphics-state internals, device APIs, refcount macros, Ghostscript memory descriptors, and filter callback definitions from `gsdfilt.h`.

## Risks

If `df->push` fails after the current device reference is incremented, the code frees the stack node but does not visibly decrement `dfs->next_device`; this should be checked against allocator/finalizer conventions. Pop executes `postpop` after stack node release, so filter implementations must not rely on stack-node state then.
