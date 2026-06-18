# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timeval_func.c

Implements helper functions for `struct timeval`.

Functions:
- `timeval_subtract(d, end, start)` computes `end - start`, borrowing from seconds if needed.
- `timeval_add(d, add)` adds another timeval into `d`, normalizing microseconds above one million.
- `timeval_divide(avg, sum, d)` divides a timeval sum by an integer denominator, carrying leftover seconds into microseconds.
- `timeval_smaller(x, y)` returns true if `x <= y` by seconds and microseconds.

Important details:
- Division by nonpositive denominator returns zero.
- Negative computed average fields are clamped to zero.
- `timeval_smaller` treats equality as smaller/true, matching histogram upper-bound insertion behavior.
- `S_SPLINT_S` guards suppress bodies for static-analysis mode.
