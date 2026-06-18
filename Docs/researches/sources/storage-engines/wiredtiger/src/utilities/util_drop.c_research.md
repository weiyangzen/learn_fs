## sources/storage-engines/wiredtiger/src/utilities/util_drop.c

Purpose: implements `wt drop`, removing a WiredTiger object by URI from the CLI.

Important APIs/types/functions: `util_drop` parses only `-?`, normalizes the single positional object through `util_uri(..., "table")`, and calls `session->drop(session, uri, "force")`.

Control flow: require one argument, allocate URI, invoke forced drop, report `session.drop: uri` on failure, free URI, and return the WiredTiger return code.

State and persistence behavior: deletes schema metadata and backing files through the session drop API. The hard-coded `force` config makes missing or partially damaged objects more permissive than a default drop, depending on library semantics.

Dependencies and integration points: uses `util_uri`, `util_err`, and public schema drop. It is dispatched after connection open and therefore observes global open modes like readonly, salvage, and recovery options.

Risks: forced drop is destructive and there is no confirmation prompt. Shorthand names default to tables. Any partial failure cleanup is delegated to WiredTiger schema code. In active systems, drop concurrency behavior is governed by the engine, not this wrapper.

Test signals: dropping an existing table, forced behavior for missing objects, readonly error propagation, shorthand and explicit URI handling, and list/reopen verification that metadata and files are gone.
