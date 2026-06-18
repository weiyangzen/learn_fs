# sources/storage-engines/foundationdb/fdbcli/CoordinatorsCommand.cpp

Purpose: Implements `coordinators`, allowing users to display cluster coordinator information or change coordinator processes and cluster description.

Important APIs/types/functions: `coordinatorsCommandActor`, private `printCoordinatorsInfo`, `changeCoordinators`, special keys `clusterDescriptionSpecialKey`, `coordinatorsAutoSpecialKey`, `coordinatorsProcessSpecialKey`, `NetworkAddress`, `Hostname`, `ManagementAPI::generateErrorMessage`, and `CoordinatorsResult`.

Control flow: With no arguments, `printCoordinatorsInfo` reads cluster description and coordinator process special keys, splits the comma-delimited process list, and prints summary information. With arguments, `changeCoordinators` extracts a single `description=` token, detects `auto`, enables special-key writes, optionally writes the description, reads auto coordinator recommendations if needed, or validates and deduplicates supplied hostnames/network addresses before writing the process list. Commit is expected to fail with `commit_unknown_result` after coordinator change; special-key failures are decoded into user-facing management errors. `NOT_ENOUGH_MACHINES` is tolerated once with a retry.

State and persistence behavior: Writes special-key-backed coordination configuration. No local persistence. The command may change the cluster file description and coordinator set, which affects cluster availability and future client connection strings.

Dependencies and integration points: Relies on special-key management API, hostname/address parsing, boost string splitting/joining, and shared coordinator keys also read by status/exclude logic.

Risks: Coordinator changes are operationally sensitive. Successful commit semantics are unusual: the code asserts if commit succeeds because coordinator changes are expected to produce unknown commit result. Duplicate detection is separated for hostnames and addresses, so semantically equivalent hostname/address pairs are not resolved. Description validation is delegated to management.

Test signals: Cover display, auto mode, manual hostnames and IP:port addresses, duplicate detection, invalid endpoint errors, description extraction, same-network no-op, not-enough-machines retry, and special-key failure message propagation.
