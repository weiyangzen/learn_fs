# File Research: sources/virtualization/guestfs-tools/builder/index-struct.c

## Scope

Memory management helpers for virt-builder parsed-index data structures.

## Behavior

- `parse_context_init` zeroes the context.
- `parse_context_free` frees the parsed index tree.
- `section_free` recursively frees a section list, section names, and fields.
- `field_free` recursively frees field lists, keys, subkeys, and values.

## Risks And Invariants

- Recursion follows linked-list `next` pointers, so parser-created chains must be acyclic.
- The functions free structure contents and nodes reachable from them; `parse_context_free` does not free the context pointer itself.
