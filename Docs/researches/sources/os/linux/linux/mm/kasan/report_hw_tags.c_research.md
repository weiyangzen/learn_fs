# File Research: sources/os/linux/linux/mm/kasan/report_hw_tags.c

## Role

Hardware tag-based KASAN report helpers. It adapts common reporting to memory tags read from hardware rather than software shadow bytes.

## Key Functions

- `kasan_find_first_bad_addr()` returns the untagged access address directly because hardware tag faults identify the failing address.
- `kasan_get_alloc_size()` scans granules with `hw_get_mem_tag()` until `KASAN_TAG_INVALID` or cache object size.
- `kasan_metadata_fetch_row()` fills a metadata row by reading hardware memory tags for each granule.
- `kasan_print_tags()` prints the pointer tag and hardware memory tag at the failing address.

## Dependencies

Uses hardware tag helpers from `kasan.h`, KASAN tag constants, memory-management headers, and slab cache object sizes.

## Research Notes

Unlike generic KASAN, hardware tag mode does not infer the first bad address by shadow walking. It trusts the hardware fault address and provides tag mismatch context for the common report printer.
