# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.h

This header defines the timer event structure and timer queue API.

Key declarations:
- `struct event`: queue link, event name, callback, callback argument, and absolute monotonic expiration.
- Timer lifecycle and queue functions: init, next timeout calculation, expiration handling, add/remove event, and reporting.

Integration:
- Shared by retransmission, SA lifetime, DPD, NAT-T, and PF_KEY notification paths.
