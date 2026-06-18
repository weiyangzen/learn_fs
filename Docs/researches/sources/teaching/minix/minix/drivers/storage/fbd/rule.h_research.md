# File Research: sources/teaching/minix/minix/drivers/storage/fbd/rule.h

## Purpose
Declares FBD rule-control and hook-dispatch functions plus shared hook mask constants.

## Contents
- `MAX_RULES` set to 16.
- Rule ioctl/matching entry points:
  - `rule_ctl()`
  - `rule_find()`
  - `rule_pre_hook()`
  - `rule_io_hook()`
  - `rule_post_hook()`
- Hook masks:
  - `PRE_HOOK`
  - `IO_HOOK`
  - `POST_HOOK`

## Integration Notes
Included by both `fbd.c` and `action.c`.

## Risks
`MAX_RULES` is compile-time fixed and shared by ioctl-visible behavior.
