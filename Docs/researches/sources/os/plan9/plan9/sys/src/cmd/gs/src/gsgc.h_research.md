# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgc.h

## Role

Library-level interface to Ghostscript garbage-collector VM spaces.

## Main Data

Defines `i_vm_space` with foreign, system, global, and local spaces. Defines `vm_spaces`, containing the GC reclaim procedure and allocator pointers accessible by indexed or named union fields.

## Main API

Defines `GS_RECLAIM` / `gs_reclaim` macros and convenience aliases such as `space_system`, `space_global`, and `spaces_indexed`.

## Dependencies

Forward-declares `gs_ref_memory_t`. Optionally checks that `r_space_bits` is 2 when visible.

## Notes

Foreign space must be index 0 because scalar PostScript refs do not need space bits for foreign/static objects. Higher-numbered VM spaces may point to lower-numbered spaces, but not vice versa.
