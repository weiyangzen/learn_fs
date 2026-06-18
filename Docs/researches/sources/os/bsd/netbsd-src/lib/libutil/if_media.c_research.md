# File Research: sources/os/bsd/netbsd-src/lib/libutil/if_media.c

## Purpose
Maps network interface media words to strings and strings back to media constants.

## Key Details
- Exposes global description tables from `IFM_*_DESCRIPTIONS`.
- Provides lookup functions for type, subtype, mode, and options.
- `get_media_option_string` consumes option bits from the caller’s media word.
- `get_media_options` parses comma-separated option names and can return the invalid token.

## Dependencies and Role
- Network utility support, not filesystem-specific.
