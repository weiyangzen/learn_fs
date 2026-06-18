# File Research: sources/teaching/minix/minix/drivers/storage/fbd/action.h

## Purpose
Declares FBD action hook functions.

## Contents
- `action_mask()`
- `action_pre_hook()`
- `action_io_hook()`
- `action_post_hook()`

## Integration Notes
Included by `rule.c`; it assumes `struct fbd_rule`, `iovec_t`, and MINIX integer types have already been made visible by included headers.

## Risks
The header has no direct include for the rule structure; include order matters.
