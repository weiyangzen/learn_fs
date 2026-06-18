# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.h

## Purpose
`frontend.h` declares the frontend process entry point and imsg dispatch/send helpers.

## Exports
- `frontend(int, int)`
- `frontend_dispatch_main`
- `frontend_dispatch_engine`
- `frontend_imsg_compose_main`
- `frontend_imsg_compose_engine`

## Integration Notes
The main process and control code use these helpers to send or route messages through the frontend.
