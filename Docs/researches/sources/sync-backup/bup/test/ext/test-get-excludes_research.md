## sources/sync-backup/bup/test/ext/test-get-excludes

Purpose: verifies contextual exclude handling for `bup get --rewrite`.

Important control flow: saves files `one`, `two`, and `three`, then rewrites with `--exclude-rx 't.*'`, with `--no-excludes`, and with multiple picks that change exclude context between destinations. It also checks that contextual arguments with no effect are rejected.

State and dependencies: temp repo, `bup get --rewrite`, and `bup ls`.

Risks covered: `rewrite.py` must invalidate directory mapping reuse when excludes change, while command parsing must reject ignored contextual options.
