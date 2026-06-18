# sources/storage-engines/foundationdb/fdbcli/ConsistencyCheckCommand.cpp

Purpose: Implements `consistencycheck [on|off]`, a small command that toggles whether consistency-checking processes are allowed to run.

Important APIs/types/functions: `consistencyCheckCommandActor(Reference<ITransaction>, tokens, bool intrans)`, `consistencyCheckSpecialKey`, `SPECIAL_KEY_SPACE_ENABLE_WRITES`, and `CommandFactory consistencyCheckFactory`.

Control flow: The actor enables special-key writes on the supplied transaction. With no arguments it reads `\xff\xff/management/consistency_check_suspended` and prints `off` when the key is present, `on` otherwise. `off` sets the key to an empty value; `on` clears it. If not already inside an fdbcli transaction (`intrans == false`), the actor commits immediately. Invalid tokens print command usage and return false.

State and persistence behavior: The persisted state is one special key. Presence means suspended/off; absence means allowed/on. In transaction mode it participates in the caller's transaction rather than committing by itself.

Dependencies and integration points: Depends on special-key-space management semantics and fdbcli transaction execution. The consistency-checking role observes this management key.

Risks: The command does not loop on retry; comments state outer fdbcli error handling is expected to print errors. This keeps behavior simple but means callers must preserve that contract. Because the toggle is inverted by key presence, future maintainers must avoid misreading the empty value as enabled.

Test signals: Tests should verify status display for present/absent key, immediate commit vs in-transaction behavior, special-key write option use, and invalid argument handling.
