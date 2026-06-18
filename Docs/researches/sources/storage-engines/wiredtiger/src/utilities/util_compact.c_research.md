## sources/storage-engines/wiredtiger/src/utilities/util_compact.c

Purpose: implements `wt compact`, exposing `WT_SESSION.compact` from the CLI for a single object URI with optional compact configuration.

Important APIs/types/functions: `util_compact` parses `-c config` and `-?`, normalizes the single positional argument through `util_uri(session, *argv, "table")`, and calls `session->compact(session, uri, config)`.

Control flow: after parsing, exactly one URI argument is required. The URI is allocated, used for the compact call, then freed. Errors are reported as `session.compact: uri`, and the function returns the WiredTiger return code.

State and persistence behavior: compaction can rewrite data files and reclaim space according to library configuration. This wrapper does not perform checkpoints or flushes itself; persistence and concurrency behavior are owned by `WT_SESSION.compact`.

Dependencies and integration points: dispatched from `util_main.c`; uses URI normalization, getopt, usage/error helpers, and the public session compact API. Global open flags such as readonly/recovery are handled before command execution.

Risks: compaction can be long-running and interacts with active database state; the CLI has no progress reporting beyond engine behavior. Passing arbitrary config strings relies on the library for validation. A shorthand name defaults to `table:`, which may surprise users intending a file URI unless they include a prefix.

Test signals: usage tests, compacting a table with and without config, invalid URI/config error propagation, readonly failure behavior, and file-size or statistics checks showing compaction did work when possible.
