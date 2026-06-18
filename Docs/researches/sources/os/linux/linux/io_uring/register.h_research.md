# File Research: sources/os/linux/linux/io_uring/register.h

Small registration header exposing shared unregister helpers.

Key responsibilities:
- Declares `io_eventfd_unregister()`.
- Declares `io_unregister_personality()` for credential personality cleanup.

Important invariant:
- These helpers operate on an existing ring context and are normally called with register-path serialization.
