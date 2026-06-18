<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_parallel_checkpoint.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_parallel_checkpoint.py

Purpose: Hook that enables WiredTiger parallel checkpoint threads for Python suite tests by appending `checkpoint_threads=<N>` to connection open configuration.

Important APIs and types: `_parse_threads` accepts no argument, a raw integer, or `threads=<N>` optionally wrapped in parentheses. `ParallelCheckpointHookCreator` stores the thread count, returns `DefaultPlatformAPI`, and registers a `wiredtiger_open` argument hook.

Control flow: The hook parses and validates a positive thread count, defaulting to four. On every `wiredtiger_open`, the argument hook converts the readonly args tuple to a list, checks whether the config already contains `checkpoint_threads=`, and appends the configured setting only when absent.

State and persistence behavior: It changes connection runtime behavior by enabling additional checkpoint worker threads. No files are written directly by the hook, but checkpoint scheduling can affect timing and persisted checkpoint state in test homes.

Dependencies and integration points: Uses the generic `wthooks.HOOK_ARGS` mechanism and `run.py --hook parallel_checkpoint[=...]`. It composes with the default platform API and other hooks that also modify open config.

Risks: String detection may miss semantically equivalent config forms or comments. More checkpoint concurrency can expose races or timing-sensitive tests. Invalid hook arguments abort hook initialization before tests run.

Test signals: Connections should open with parallel checkpoint configuration unless already explicit; tests should either pass under extra checkpoint concurrency or reveal checkpoint-thread-sensitive bugs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_parallel_checkpoint.py -->
