# sources/storage-engines/foundationdb/fdbcli/TssqCommand.cpp

## Purpose

`TssqCommand.cpp` implements `fdbcli tssq`, a command for listing, starting, and stopping quarantine mode for Testing Storage Server (TSS) processes. It is operational tooling for cases where a TSS has incorrect data or needs manual investigation.

## Important APIs, Types, and Functions

- `tssqCommandActor(Reference<IDatabase>, std::vector<StringRef>)` validates grammar and dispatches subcommands.
- `tssQuarantineList` reads `tssQuarantineKeys` and prints quarantined TSS IDs.
- `tssQuarantine` validates a target storage ID, toggles its quarantine key, and updates the TSS mapping.
- `serverListKeyFor`, `decodeServerListValue`, `StorageServerInterface::isTss`, `tssQuarantineKeyFor`, `decodeTssQuarantineKey`, `tssMappingKeys`, and `KeyBackedMap<UID, UID>` are the relevant metadata APIs.
- `CommandFactory tssqFactory` registers the command.

## Control Flow

`tssq list` calls `tssQuarantineList`, which reads the full quarantine key range with system-key access and asserts it is not paginated. `tssq start <StorageUID>` and `tssq stop <StorageUID>` require a 32-hex-character UID. `tssQuarantine` first checks that the UID exists in the server list, then decodes the `StorageServerInterface` and rejects non-TSS storage IDs. It then checks the current quarantine key to avoid duplicate start or invalid stop. Starting sets the quarantine key and removes the TSS pair mapping; stopping clears the quarantine key. The transaction commits and the command prints success.

## State and Persistence Behavior

The command writes system metadata under the TSS quarantine keyspace. Starting quarantine also erases the TSS's pair mapping from `tssMappingKeys`, which disconnects it from the active TSS pairing metadata. Stopping only clears quarantine; the command text notes that removing quarantine can destroy the TSS process, but that operational effect happens elsewhere in the cluster.

## Dependencies and Integration Points

This file integrates with server-list metadata, TSS mapping metadata, key-backed maps, system-key transactions, and fdbcli dispatch. All database operations use `ACCESS_SYSTEM_KEYS` and `PRIORITY_SYSTEM_IMMEDIATE`.

## Risks and Edge Cases

The list path uses `CLIENT_KNOBS->TOO_MANY` and asserts no pagination, which assumes quarantine cardinality stays small. `std::all_of(..., &isxdigit)` passes raw chars to `isxdigit`; this is conventional here but can be unsafe for negative signed chars outside ASCII. `tssQuarantine` relies on `ssi.tssPairID` being present for TSS interfaces when erasing the mapping.

## Test Signals

The listed integration test file does not include an active `tssq` test. Good signals would cover listing empty/non-empty quarantine, rejecting malformed UIDs, rejecting non-TSS storage IDs, duplicate start/stop behavior, and confirming the quarantine key and TSS mapping mutation.
