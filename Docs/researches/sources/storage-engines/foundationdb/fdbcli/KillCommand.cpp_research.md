# sources/storage-engines/foundationdb/fdbcli/KillCommand.cpp

Purpose: Implements `kill`, allowing operators to list killable processes from cached worker interfaces and send reboot-worker kill requests to selected or all processes.

Important APIs/types/functions: `killCommandActor(Reference<IDatabase>, Reference<ITransaction>, tokens, address_interface)`, `getWorkerInterfaces`, `db->rebootWorker(addresses, false, 0)`, `killGenerator`, and `CommandFactory killFactory`.

Control flow: With only `kill`, the command refreshes the address cache from worker interfaces. With `kill` or `kill list`, it prints cached addresses. `kill all` requires a populated cache, joins all addresses, and sends one reboot request. Explicit addresses are validated against the cache before sending one request. After a successful explicit kill, the actor waits three seconds so the network queue can flush before the client exits.

State and persistence behavior: No cluster metadata is written by this file, but it sends kill/reboot requests to live processes. The address map is transient state owned by the caller and must be refreshed before use.

Dependencies and integration points: Integrates with worker interface special keys, database reboot API, boost string join, fdbcli completion generator, and command help.

Risks: Operationally disruptive. Cache staleness can cause false rejections or missed processes. `kill all` can terminate every known process. The command relies on the reboot API returning a nonzero count to indicate request dispatch.

Test signals: Cover cache population/listing, empty-cache `all` error, explicit unknown address error, all/explicit successful batching, zero requests sent, three-second delay behavior under test control, and completion suggestions.
