# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpm.h

## Role

`gscpm.h` defines enum values for charpath mode and cache-device status in Ghostscript.

This is text/rendering state infrastructure, not filesystem code.

## Main Definitions

`gs_char_path_mode` values:

- `cpm_show`
- `cpm_charwidth`
- `cpm_false_charpath`
- `cpm_true_charpath`
- `cpm_false_charboxpath`
- `cpm_true_charboxpath`

`gs_in_cache_device_t` values:

- `CACHE_DEVICE_NONE`
- `CACHE_DEVICE_NOT_CACHING`
- `CACHE_DEVICE_NONE_AND_CLIP`
- `CACHE_DEVICE_CACHING`

## Important Contracts

Both default enum values are explicitly required to remain zero.

## Dependencies

No substantial dependencies beyond standard Ghostscript type context.

## Notable Risks

Enums are used as shared state markers; changing numeric order would break callers relying on zero/default semantics.
