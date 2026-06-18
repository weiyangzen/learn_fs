# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsgdata.c

## Role

Implementation of glyph data ownership, substring, and freeing helpers.

## Main Data

Defines the GC descriptor for `gs_glyph_data_t`, permanent no-free procedures, and font-allocator-backed free/substring procedures.

## Control Flow

`gs_glyph_data_substring` range-checks and dispatches to the current glyph-data procs. `gs_glyph_data_free` dispatches free and resets the object to null. Permanent glyph data simply adjusts pointer/size. Font-owned string data may be memmoved and resized when substringed; object-backed bytes use permanent substring behavior. Constructors initialize glyph data from strings, byte objects, or null and select either no-free or font-backed procs.

## Dependencies

Uses Ghostscript bytestring helpers, font memory, GC descriptors, and error APIs.

## Notes

When initialized with a non-null font, callers transfer ownership of allocated glyph bytes to the glyph data object until `gs_glyph_data_free`.
