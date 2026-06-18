# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/app.h

This header declares the `isakmpd` application wrapper API.

Key contents:
- Include guard `_APP_H_`.
- Extern declarations for `app_socket` and `app_none`.
- Function prototypes for `app_init()` and `app_handler()`.

Research notes:
- This header exposes only the small application-channel lifecycle used by the daemon event loop.
