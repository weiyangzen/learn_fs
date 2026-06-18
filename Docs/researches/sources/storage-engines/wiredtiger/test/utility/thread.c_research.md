# sources/storage-engines/wiredtiger/test/utility/thread.c

## Purpose
`thread.c` implements reusable thread bodies and event handlers for WiredTiger stress tests. It provides one append worker for variable-length column stores and several simple API-operation workers originally built for `test/fops`, exercising creates, drops, cursors, and bulk cursor races against checkpoints.

## Important APIs and functions
Exported functions are `thread_append`, `handle_op_error`, `handle_op_message`, `op_bulk`, `op_bulk_unique`, `op_cursor`, `op_create`, `op_create_unique`, and `op_drop`. All operation workers accept `TEST_PER_THREAD_OPTS *` except `thread_append`, which accepts `TEST_OPTS *`.

## Control flow and behavior
`thread_append` opens a session and append cursor, inserts formatted values until `opts->running` becomes false, and lets thread id zero update `opts->max_inserted_id` and terminate after `nrecords`. The operation workers open a session, perform one API sequence, tolerate expected racing errors such as `EEXIST`, `ENOENT`, `EBUSY`, and selected `EINVAL`, close resources, and increment `thread_counter`. The unique variants create object names using atomic `unique_id`, then drop them with randomly chosen forced or checkpoint-wait-disabled config.

## State, dependencies, and integration
Shared mutable state includes `opts->running`, `opts->next_threadid`, `opts->max_inserted_id`, `opts->unique_id`, and per-thread `thread_counter`. The code depends on WiredTiger connection/session/cursor APIs, atomic helpers, random helpers, yielding, and `DEFAULT_TABLE_SCHEMA`. The event handlers integrate with tests that intentionally provoke expected failures and need to suppress noisy error/message output.

## Risks and test signals
Risks are intentional races, non-atomic reads/writes of some shared flags, ignored return values in optional data insertion, and reliance on exact error-code behavior from checkpoint/cursor/drop races. Useful signals are stress tests such as checkpoint operation races completing without unexpected `testutil_die`, operation counters increasing during expected `EBUSY` loops, no leaked sessions/cursors, and append workers stopping at the configured record threshold.
