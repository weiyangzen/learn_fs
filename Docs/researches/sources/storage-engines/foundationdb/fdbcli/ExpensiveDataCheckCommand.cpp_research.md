# sources/storage-engines/foundationdb/fdbcli/ExpensiveDataCheckCommand.cpp

Purpose: Implements hidden `expensive_data_check`, which triggers process reboot with the check flag enabled so selected processes perform expensive data checking on restart.

Important APIs/types/functions: `expensiveDataCheckCommandActor(Reference<IDatabase>, Reference<ITransaction>, tokens, address_interface)`, `getWorkerInterfaces`, `db->rebootWorker(addresses, true, 0)`, and the cached `address_interface` map from process address key to worker interface metadata.

Control flow: With no arguments, the command refreshes the process-address map and lists checkable addresses. `list` prints the cached map. `all` requires a populated cache, joins all cached addresses with commas, and calls `rebootWorker` once so requests are sent in parallel. Explicit address arguments are validated against the cached map before joining and sending one reboot/check request. Errors instruct users to refresh the list.

State and persistence behavior: The command itself keeps transient state in the caller-owned `address_interface` cache across invocations. It does not write FoundationDB keys, but it sends reboot requests to cluster workers, causing process restarts and subsequent data checking.

Dependencies and integration points: Shares cache behavior with `kill`/`suspend`, depends on worker interface discovery through special keys, and uses the database client API reboot path.

Risks: Operationally disruptive: it kills processes. Cached addresses can become stale; validation intentionally requires an earlier list refresh. Curly apostrophes in some error strings are harmless but worth preserving/normalizing consistently if CLI output tests are strict. `all` can affect every known process at once.

Test signals: Cover initial listing, empty cache errors, stale/unknown address validation, `all` batching, explicit address batching, zero requests sent, and integration with worker-interface verification.
