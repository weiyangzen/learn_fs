# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.h

## Purpose
Declares sparse interval bitmap APIs for 64-bit and 32-bit ranges.

## Key Structures
- `struct xbitmap64`: cached rb-root storing 64-bit intervals.
- `struct xbitmap32`: cached rb-root storing 32-bit intervals.

## API Contracts
Iterator callbacks return 0 to continue and nonzero to stop; the stop value is propagated. Callers must not mutate a bitmap while walking it. `-ECANCELED` is documented as a safe sentinel for intentional cancellation because the bitmap walkers do not generate it themselves.

## Notes
This generic header underlies typed scrub bitmaps such as AG block, fsblock, and agino bitmap wrappers.
