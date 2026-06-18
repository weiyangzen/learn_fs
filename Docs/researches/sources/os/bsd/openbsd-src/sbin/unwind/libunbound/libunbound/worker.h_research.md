# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/worker.h

Declares worker callback and network service interfaces shared by libunbound worker code and daemon worker code.

Main declarations:
- `libworker_send_query()` and `worker_send_query()` send module-serviced outbound queries to authoritative/upstream servers.
- `libworker_handle_service_reply()` and `worker_handle_service_reply()` process network replies.
- `libworker_handle_control_cmd()` and `worker_handle_control_cmd()` process tube control messages.
- Foreground, background, and event mesh completion callbacks for libworker.
- Daemon worker callbacks for signal handling, client request handling, allocation cleanup, statistics/probe timers, accept start/stop, and remote-control accept/data handling.
- `remote_get_opt_ssl()` prints option values over SSL remote-control paths.

Role:
- Provides a common function-pointer surface expected by module code and callback whitelists.
- In `libworker.c`, daemon-only symbols are implemented as assertion stubs because the library worker does not accept client-facing daemon traffic.
