# sources/storage-engines/foundationdb/fdbcli/SuspendCommand.cpp

Purpose: Implements `suspend`, allowing operators to ask selected processes to suspend for a duration and then die.

Important APIs/types/functions: `suspendCommandActor(Reference<IDatabase>, Reference<ITransaction>, tokens, address_interface)`, `getWorkerInterfaces`, `db->rebootWorker(addresses, false, seconds)`, and `CommandFactory suspendFactory`.

Control flow: With no args, the command refreshes and prints suspendable process addresses. With only a duration token, usage is printed. With duration plus addresses, it validates every address against the cached map, parses seconds using `sscanf` with full-token validation, joins addresses with commas, and sends a reboot-worker request with the suspend duration. It prints attempted count on success or an error suggesting the list be refreshed if no requests were sent.

State and persistence behavior: No metadata is persisted by the command. It uses a transient caller-owned address cache and sends process-control requests that affect live workers.

Dependencies and integration points: Shares worker interface cache behavior with `kill` and `expensive_data_check`, uses boost join and the database reboot API, and depends on fdbcli command dispatch.

Risks: Operationally disruptive. Requires a populated, current address cache; stale cache can reject valid targets or send to outdated addresses. Seconds are cast to `int`, so fractional values are truncated and very large values may overflow. Negative durations are not explicitly rejected.

Test signals: Cover list population, missing address cache, invalid/negative/fractional/large seconds, unknown addresses, successful batching, zero requests sent, and process-control integration behavior.
