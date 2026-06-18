# sources/user-network-fs/nfs-utils/utils/gssd/svcgssd.h

Purpose: this header defines the minimal shared server gssd interface.

Important APIs and types: it includes GSSAPI and queue/type headers, declares `void handle_nullreq(char *cp);`, and defines `GSSD_SERVICE_NAME` as `"nfs"`. The function is implemented in `svcgssd_proc.c` and invoked by the event callback in `svcgssd.c`.

Control flow and integration: the header couples the daemon entrypoint to the null RPC processor without exposing internal credential or downcall structures. `GSSD_SERVICE_NAME` is used when `svcgssd` acquires default hostbased service credentials.

State and persistence: no state is owned here; it exposes a contract around mutable text input from the kernel init channel.

Dependencies: GSSAPI is included because the surrounding server gssd code shares GSS type vocabulary, though this header itself exports only a char-pointer request handler and a service-name macro.

Risks: the interface does not describe buffer ownership or syntax, so callers must already know the qword-encoded kernel channel format. Test signals are compile coverage for both `svcgssd.c` and `svcgssd_proc.c`, plus malformed null request tests that verify the handler tolerates bad input.
