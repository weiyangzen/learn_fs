# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/cookie.h

This header declares the cookie generation interface.

Key contents:
- Forward declarations for `struct exchange` and `struct transport`.
- Prototype for `cookie_gen`.

Research notes:
- The header keeps cookie generation independent from full transport/exchange definitions.
