# File Research: sources/virtualization/spdk/lib/event/Makefile

Builds the SPDK event library.

Important behavior:
- Declares shared object version `16.0`.
- Adds environment CFLAGS and suppresses packed-member address warnings.
- Builds `app.c`, `reactor.c`, `log_rpc.c`, `app_rpc.c`, and `scheduler_static.c`.
- Uses `spdk_event.map` as the library version/map file.
- Includes the common SPDK library make rules.

Role: groups the application framework, reactor runtime, logging RPCs, framework RPCs, and static scheduler into `libspdk_event`.
