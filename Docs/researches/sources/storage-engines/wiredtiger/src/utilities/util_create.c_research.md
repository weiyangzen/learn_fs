## sources/storage-engines/wiredtiger/src/utilities/util_create.c

Purpose: implements `wt create`, creating a WiredTiger object from the CLI with optional session create configuration.

Important APIs/types/functions: `util_create` parses `-c config`, normalizes the single positional name with `util_uri(..., "table")`, and invokes `session->create(session, uri, config)`. `usage` documents `create [-c configuration] uri`.

Control flow: option parse, require exactly one argument, allocate normalized URI, call create, report `session.create: uri` on error, free URI, return the WiredTiger status.

State and persistence behavior: creates table/file/tiered/etc metadata and associated objects through the session API. `util_main.c` opens the connection with `create` config for this command, so the database home can be initialized if needed.

Dependencies and integration points: uses `util_uri` defaulting to table, `util_err`, and `WT_SESSION.create`. The broader create semantics depend on schema, metadata, logging, and recovery settings configured when the connection was opened.

Risks: defaulting unprefixed names to `table:` is convenient but requires explicit prefixes for other object types. Arbitrary config is passed through without CLI-level filtering. Failure after partial schema creation is handled by library schema code, not the wrapper.

Test signals: creating default table names, explicit URI prefixes, invalid config failures, create in a new home, duplicate object errors, and successful reopen/list after create.
