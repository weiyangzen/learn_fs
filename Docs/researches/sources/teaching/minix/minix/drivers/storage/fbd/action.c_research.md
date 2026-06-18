# File Research: sources/teaching/minix/minix/drivers/storage/fbd/action.c

## Purpose
Implements the concrete fault-injection actions used by FBD rules.

## Key Behavior
- `action_mask()` maps action type to hook phases:
  - corrupt: I/O hook;
  - error: pre and post hooks;
  - misdirect: pre hook;
  - lost/torn write: pre and post hooks.
- Corruption action can zero data, generate persistent deterministic `offset ^ 0xdeadbeef` patterns, or fill bytes randomly.
- Error action trims a request to the bytes before the matching range, then converts successful completion to the configured error code.
- Misdirection action randomizes the request position within a configured aligned range.
- Lost/torn action truncates the request to a configured leading byte count but reports full original completion on success.
- `get_range()` calculates the overlapping subrange affected by a rule and handles `end <= start` as “to EOF.”
- `limit_range()` shrinks an iovec array to a target byte count.

## Integration Notes
Called only through `rule.c` hook dispatch. It depends on `struct fbd_rule` and action parameter layouts from `<sys/ioc_fbd.h>`.

## Risks
Persistent corruption assumes dword-aligned positions and sizes. Misdirection cannot represent “to real end of disk” because the action layer has no disk-size knowledge.
