# File Research: sources/local-fs/mtd-utils/include/common.h

## Purpose
Common utility macros and inline helpers used across `mtd-utils`.

## Key Elements
Provides min/max/alignment helpers, off_t printf format macros, standard message/error/warning macros, a fallback `rpmatch`, `prompt`, `is_power_of_2`, simple full-string numeric parsers, and `common_print_version`.

## Dependencies
Requires `PROGRAM_NAME` to be defined before inclusion and includes generated `version.h` plus `xalloc.h`.

## Behavior/Risks
Uses GNU C statement expressions and `typeof`. `prompt` defaults to the provided answer when input cannot be read.
