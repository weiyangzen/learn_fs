# sources/storage-engines/foundationdb/fdbcli/SnapshotCommand.cpp

Purpose: Implements hidden `snapshot`, which sends a snapshot command string to all relevant processes through the database API and reports a generated UID for cleanup correlation.

Important APIs/types/functions: `snapshotCommandActor(Reference<IDatabase>, tokens)`, `deterministicRandom()->randomUniqueID`, `Standalone<StringRef>`, `db->createSnapshot(uid, snap_cmd)`, and `CommandFactory snapshotFactory`.

Control flow: The actor requires at least one argument after `snapshot`. It generates a UID string, concatenates all remaining tokens with spaces into `snap_cmd`, calls `createSnapshot`, and prints success with the UID. Errors are caught locally, printed with error code/name and cleanup guidance referencing the UID, and return false.

State and persistence behavior: No local persistence. Snapshot side effects occur on cluster/process storage as implemented by the database API. The generated UID is not stored locally but is essential for manual cleanup if partial snapshots were created.

Dependencies and integration points: Depends on fdbclient snapshot API and hidden fdbcli command dispatch. Operationally tied to instance-level snapshot implementations.

Risks: Hidden but potentially disruptive. Token concatenation preserves spaces between tokens but not original quoting details. Failure may leave external snapshots requiring manual cleanup. Validation of snapshot subcommand semantics is delegated to server-side API.

Test signals: Cover missing args, command string construction, success UID output, API error output including cleanup UID, and quoted/multi-token snapshot command behavior in the top-level parser.
