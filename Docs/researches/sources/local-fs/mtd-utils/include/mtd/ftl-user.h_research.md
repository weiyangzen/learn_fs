# File Research: sources/local-fs/mtd-utils/include/mtd/ftl-user.h

## Purpose
Userspace definitions for legacy Flash Translation Layer metadata.

## Key Elements
Defines `erase_unit_header_t`, header flags, and block allocation macros/constants for free, deleted, control, data, replacement, and bad blocks.

## Dependencies
Uses `u_int*` typedefs from system headers included by callers.

## Behavior/Risks
Represents old on-flash FTL layout used by `ftl_check` and `ftl_format`; packed/endianness handling is left to callers.
