# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/istack.c

Purpose: implements expandable interpreter stacks of refs, used for Ghostscript operand, execution, and dictionary stacks.

Main operations:
- `ref_stack_init` initializes a stack over an initial ref-array block, allocates parameter storage if needed, sets guards, initializes null body slots, and records allocator/max-stack state.
- `ref_stack_set_max_count`, `ref_stack_set_margin`, and `ref_stack_allow_expansion` adjust stack limits and expansion policy.
- `ref_stack_count`, `ref_stack_index`, and `ref_stack_counttomark` inspect stack contents across linked blocks.
- `ref_stack_store_check` and `ref_stack_store` copy stack ranges into arrays while enforcing VM-space store rules and save/undo semantics.
- `ref_stack_push`, `ref_stack_extend`, `ref_stack_push_block`, `ref_stack_pop`, and `ref_stack_pop_block` manage linked-block growth and shrinkage.
- Enumeration and cleanup routines support GC scanning, and release/free routines tear down all stack blocks.

Block behavior:
- Stack blocks are represented as `t_array` objects whose first refs store `next` and `used` metadata.
- Pushing a new block keeps roughly one third of the current top block, moves the rest into the lower block's `used` interval, and nulls unused areas.
- Popping can either merge two blocks and free the top block or move data upward if both blocks do not fit together.

GC support relocates current block refs and adjusts raw stack pointers by the packed-ref relocation delta.
