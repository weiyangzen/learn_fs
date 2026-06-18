# sources/user-network-fs/samba/source4/lib/messaging/messaging_internal.h

`messaging_internal.h` defines the private layout of `struct imessaging_context` and declares `imessaging_register_extra_handlers()`. The context links all live messaging contexts, stores the owning `tevent_context`, local `server_id`, socket and lock directories, fixed and temporary dispatch registries, IRPC registration list, pending IRPC request IDR, `server_id_db` name store, start time, datagram reference, and incoming-listener accounting.

This header is the shared contract between `messaging.c`, `messaging_send.c`, `messaging_handlers.c`, and the Python binding. The most important state behavior is the split between normal and discard-incoming contexts: discard contexts start with zero listeners but pending IRPC calls temporarily add listeners so replies can be received. The global context list enables fork reinitialization and event-context datagram unref.

Risks are ABI and encapsulation related. Because the Python module includes this private header to access `msg_ctx->ev`, changes to the structure can break bindings. Listener count, IDR cleanup, and datagram reference ownership must stay consistent with destructors and reinit code. Test coverage should exercise free-during-callback and fork/reinit paths.
