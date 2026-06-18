# sources/object-store/garage/src/garage/cli/remote/block.rs

Purpose: implements remote CLI block diagnostics and repair controls.

Important APIs/types/functions: `Cli::cmd_block`, `cmd_list_block_errors`, `cmd_get_block_info`, `cmd_block_retry_now`, `cmd_block_purge`, and `deleted_to_str`.

Control flow: list errors calls local admin API on the selected node and formats RC/error/backoff age. Info fetches block references, prints version/upload backlinks, detects inconsistencies between block refs and versions, and warns when refcount differs from active reference count. Retry accepts either `--all` or explicit hashes. Purge requires `--yes` and sends block purge request.

State and persistence: retry mutates resync queue/backoff state; purge can delete block refs, versions, objects, and multipart uploads through admin API. Info/list are read-only.

Dependencies and integration points: uses local API wrapper, admin API request types, `format_table`, `timeago`, and CLI structs. Connects directly to block manager/resync admin surfaces.

Risks: purge is destructive and guarded only by `--yes`; callers must provide correct block hashes. Info warnings depend on response consistency fields and may not catch every metadata issue.

Test signals: no direct tests; admin API tests and manual operational checks should cover block info/error/retry/purge.
