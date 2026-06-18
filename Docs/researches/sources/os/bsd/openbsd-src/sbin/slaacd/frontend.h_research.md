# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.h

Declares the frontend process API:
- `frontend(int, int)`: child-process entry point.
- `frontend_dispatch_main(...)`: imsg dispatch from main.
- `frontend_dispatch_engine(...)`: imsg dispatch from engine.
- `frontend_imsg_compose_main(...)`: send imsg to main.
- `frontend_imsg_compose_engine(...)`: send imsg to engine with peer/pid metadata.

Role:
- Shared declaration boundary for `slaacd.c`, `frontend.c`, and control code.
- Captures the daemon’s three-process imsg topology.
