# sources/security-integrity/selinux/libsepol/src/util.c

## Purpose
`util.c` contains general libsepol utilities for dynamic integer arrays, formatting access vectors and extended permissions, and tokenizing strings without `sscanf`.

## Important APIs and Control Flow
`add_i_to_a()` appends a `uint32_t` to a resized array. `sepol_av_to_string()` formats permission bits for a class by mapping values back to class-specific and common permission names. `sepol_extended_perms_to_string()` formats ioctl or netlink xperm bitmaps and compresses adjacent bits into ranges. `tokenize()` splits a line into allocated fields and leaves the final argument as the remainder.

## Dependencies and Integration
The formatting helpers are used by diagnostics in services and tooling. The file depends on policydb class structures, hashtab mapping, xperm macros, and `private.h`.

## Risks and Test Signals
`add_i_to_a()` reallocates on every append. Callers own token strings, including partial outputs on failure. `sepol_av_to_string()` assumes a valid class index. Tests should cover common/class permission formatting, long names and resize, xperm singleton/range compression, delimiter behavior, and allocation failures.
