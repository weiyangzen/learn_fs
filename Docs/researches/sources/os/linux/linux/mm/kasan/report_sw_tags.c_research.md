# File Research: sources/os/linux/linux/mm/kasan/report_sw_tags.c

## Role

Software tag-based KASAN report helpers. It bridges common report printing to tag values stored in software shadow memory.

## Key Functions

- `kasan_find_first_bad_addr()` compares the pointer tag with shadow tag bytes and returns the first granule whose memory tag differs.
- `kasan_get_alloc_size()` scans software shadow tags until `KASAN_TAG_INVALID`.
- `kasan_metadata_fetch_row()` copies software tag shadow bytes for the metadata dump.
- `kasan_print_tags()` prints pointer tag and shadow memory tag.
- Under `CONFIG_KASAN_STACK`, `kasan_print_address_stack_frame()` prints basic current-task stack ownership.

## Dependencies

Uses KASAN tag helpers, shadow mapping, stack/task helpers, slab internals, and common KASAN report structures.

## Research Notes

Software tag reporting is less semantically rich than generic shadow reporting: tag mismatch establishes invalid access, while allocation/free classification comes from the shared tag-mode stack ring in `report_tags.c`.
