# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/engine.h

Declares the engine-facing imsg payloads and public engine entry points.

Contents:
- `struct imsg_configure_address`: interface index, IPv6 address, gateway/source router, prefix mask, valid/preferred lifetimes, MTU, and temporary-address flag.
- `struct imsg_configure_dfr`: interface index, routing domain, gateway address, and router lifetime for default route management.
- `engine(int, int)`: child-process entry point.
- `engine_imsg_compose_frontend(...)`: helper for sending imsgs from engine to frontend.

Role:
- Defines the contract between `engine.c` and `slaacd.c` for privileged address/route configuration.
- Keeps kernel mutation details out of the engine; the engine sends typed proposals and the main process performs syscalls/ioctls.
