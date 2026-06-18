# File Research: sources/os/bsd/freebsd-src/sys/sys/_pv_entry.h

Physical-to-virtual page mapping entry structures.

Key elements:
- Defines `pv_entry_t`, representing a virtual mapping of a VM page.
- Defines per-pmap `pv_chunk` storage sized to one page.
- Computes `_NPCPV`, `_NPCM`, `PC_FREEN`, and `PC_FREEL` from page size and word width.
- Provides kernel inline helpers `pc_is_full`, `pc_is_free`, `pv_to_chunk`, and `PV_PMAP`.

Dependencies:
- Includes `sys/param.h`.
- Requires VM/page types and queue macros from included context.

Research notes:
- Enforces `sizeof(struct pv_chunk) == PAGE_SIZE`.
- Important VM infrastructure for page mappings that back filesystem cache and memory-mapped files.
