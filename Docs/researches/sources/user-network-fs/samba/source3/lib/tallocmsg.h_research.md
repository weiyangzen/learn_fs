## sources/user-network-fs/samba/source3/lib/tallocmsg.h

Purpose: public declaration for registering the talloc pool usage messaging handler.

Important API: `register_msg_pool_usage(TALLOC_CTX *mem_ctx, struct messaging_context *msg_ctx)`. It forward-declares `struct messaging_context` and includes `replace.h`/`talloc.h` for base types.

Control flow contract: callers with a messaging context call the function during process initialization. The implementation installs a long-lived filtered read request that listens for `MSG_REQ_POOL_USAGE` and writes reports to a received fd.

State and persistence: the header exposes no state. Lifetime is controlled by the passed talloc context in the implementation. Integration points are Samba messaging setup and diagnostic tooling that sends the request message.

Risks and tests: callers must ensure the `mem_ctx` outlives the desired diagnostic registration. The API has no return value, so registration failure is only logged. Test signals should validate that services register it at startup where expected and that failure to register does not break service operation.
