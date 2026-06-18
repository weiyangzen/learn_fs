<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_disagg.py -->
# sources/storage-engines/wiredtiger/test/suite/hooks/hook_disagg.py

Purpose: Hook that runs ordinary Python tests against disaggregated/layered storage by injecting page-log configuration, translating eligible table URIs, and skipping unsupported operations.

Important APIs and types: `wiredtiger_open_replace`, URI helpers `mark_as_layered`, `is_layered`, `replace_uri`, replacements for session `alter`, `checkpoint`, `compact`, `create`, `drop`, `open_cursor`, `salvage`, `truncate`, and `verify`, `DisaggHookCreator`, and `DisaggPlatformAPI`.

Control flow: The open replacement validates page-log/key-provider extensions, rejects incompatible connection configs, merges `verbose=[layered]`, builds `disaggregated=(role=...,page_log=...)`, loads extensions, records leader/follower role on the testcase, calls original open, and ignores expected disagg output. `session_create_replace` marks eligible row-store tables layered, either rewrites `table:` to `layered:` or appends layered block-manager config, then rejects indexes/log/import cases that are unsupported.

State and persistence behavior: Per-testcase sets `layered_uris` and `non_layered_uris` drive later URI rewriting. Persistent data may be stored through page-log/layered objects rather than normal `.wt` files; `tableExists` returns false and `initialFileName` returns `None` because local file mapping is not equivalent.

Dependencies and integration points: Uses `helper_disagg` storage discovery/output filters, `wthooks.DisaggParameters`, `WiredTigerTestCase.findExtension`, command-line var `page_log`, and hook platform API methods consumed by `wttest` and datasets.

Risks: URI tracking lives on the testcase rather than connection, so multiple homes/connections can confuse state. Config parsing is string/regex based and does not handle arbitrary nesting. Many unsupported features are skipped at runtime, so coverage is intentionally partial.

Test signals: Successful disagg runs show layered URI tracking, no unsupported-operation execution, expected verbose-output filtering, and normal suite assertions against layered data.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/hooks/hook_disagg.py -->
