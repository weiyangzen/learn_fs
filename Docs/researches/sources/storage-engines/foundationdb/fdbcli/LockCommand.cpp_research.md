# sources/storage-engines/foundationdb/fdbcli/LockCommand.cpp

Purpose: Implements database `lock` and `unlock` support using a special key that stores a lock UID.

Important APIs/types/functions: `lockCommandActor`, private `lockDatabase`, exported `unlockDatabaseActor`, `lockSpecialKey`, `deterministicRandom()->randomUniqueID`, and `CommandFactory` registrations for `lock` and `unlock`.

Control flow: `lock` requires no extra tokens, generates a random UID, prints it, and calls `lockDatabase`. `lockDatabase` enables special-key writes, sets `\xff\xff/management/db_locked` to the UID string, commits with retry, returns special-key failure messages, and rethrows `database_locked`. `unlockDatabaseActor` reads the lock key, returns true if absent, compares the stored UID with the provided UID, clears the key on match, commits, and handles special-key failures.

State and persistence behavior: The lock state is a persisted management special key containing the UID string. Unlock requires exact UID match. No local state is persisted.

Dependencies and integration points: Depends on special-key-space lock management and fdbcli higher-level confirmation for unlock, as implied by help text. Locking affects database operations beyond fdbcli.

Risks: Losing the printed UID prevents normal unlock through this command. The file does not itself prompt for unlock confirmation; that must be enforced by dispatch. `UID::fromString` on stored values assumes valid lock metadata.

Test signals: Cover lock success, already-locked error propagation, special-key failure message, unlock absent key, wrong UID, correct UID, malformed stored UID, and retry behavior.
