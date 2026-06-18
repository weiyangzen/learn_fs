# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_rate.c

## Purpose

`kern_rate.c` provides simple kernel rate-limiting helpers.

## Functions

- `ratecheck(struct timeval *lasttime, const struct timeval *mininterval)`
  - Uses `getmicrouptime()`.
  - Allows an event if elapsed time since `lasttime` is at least `mininterval`.
  - Also allows the first event when `lasttime` is zero.
  - Updates `lasttime` on allow.
- `ppsratecheck(struct timeval *lasttime, int *curpps, int maxpps)`
  - Implements per-second event/packet rate limiting.
  - Resets the current counter when first called or when at least one second has elapsed.
  - Allows all events if `maxpps < 0`.
  - Allows while `*curpps < maxpps`.
  - Always increments `curpps` unless already `INT_MAX`, allowing callers to use the counter for statistics without integer wraparound.

## Notes

These helpers are generic and appear in many kernel subsystems for suppressing repeated logs or throttling event handling.
