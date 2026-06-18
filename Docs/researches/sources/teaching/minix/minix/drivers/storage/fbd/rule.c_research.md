# File Research: sources/teaching/minix/minix/drivers/storage/fbd/rule.c

## Purpose
Maintains FBD rule storage, ioctl control, rule matching, match lifetime counters, and hook dispatch.

## Key Behavior
- Stores up to `MAX_RULES` active rules in a static array.
- `FBDCADDRULE` finds a free slot, copies in a full rule, assigns a 1-based rule number, and returns it.
- `FBDCDELRULE` copies in a rule number and clears that slot.
- `FBDCGETRULE` copies in a requested rule number from the struct offset and copies out the full active rule.
- Matching requires range overlap and matching read/write flags.
- `skip` delays activation by decrementing on matches until zero.
- `count` decrements on triggered matches and disables the rule when it reaches zero.
- Matching rules are stored in `matches[]` for the subsequent pre/I/O/post hook calls of the same request.

## Integration Notes
Uses `action_mask()` to combine required hook phases and action hook functions to mutate request state or data.

## Risks
`matches[]` is global per request; the driver is synchronous, so that is acceptable only as long as requests are not processed concurrently. Rule counters mutate during matching, not after successful lower I/O.
