# File Research: sources/os/linux/linux/mm/bootmem_info.c

## Purpose
Tracks boot-time memory-management metadata pages so memory hotplug can later identify and release reserved metadata such as node info and sparsemem section usage.

## Main Interfaces
- `get_page_bootmem()` tags a metadata page with bootmem type and info encoded in `page_private`, marks it private, and increments its reference count.
- `put_page_bootmem()` drops a tagged bootmem page reference and frees the reserved page when the last metadata reference is gone.
- `register_page_bootmem_info_node()` registers pgdat pages and sparsemem section metadata pages for a node.

## Control Flow
Node registration tags the physical pages backing `struct pglist_data`, then walks section-sized PFN ranges for the node. Valid PFNs owned by the node are aligned to section boundaries and registered through `register_page_bootmem_info_section()`, which also registers vmemmap memmap pages unless preinitialized and tags `mem_section_usage` pages.

## State And Synchronization
The file relies on early boot/hotplug context rather than local locking. Encoded `page_private` stores the bootmem type in low bits and node/section info above it.

## Integration Points
Uses memblock/sparsemem section metadata, memory hotplug bootmem type definitions, kmemleak physical-part freeing, reserved-page freeing, and node PFN ownership helpers.

## Risks And Review Focus
- Type/info encoding must stay within the low-nibble layout expected by bootmem helpers.
- Duplicate registration across nodes is avoided with `early_pfn_to_nid()` and is important on platforms with overlapping node PFN assignments.
