<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multiversion.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/multiversion.py

Purpose: simple Workgen insert example with optional WiredTiger compatibility configuration for older release testing.

Important APIs and functions: local `show(tname, s)` and `create_compat_config(args)`. Adds `--release` argument with choices `4.2` and `4.4`, calls `context.initialize()` before opening, and uses `Operation.OP_INSERT`.

Control flow: parse release argument; open a 1 GB cache WT home with compatibility suffix based on release; create `table:simple`; run one append insert workload, show contents; run five more inserts and show contents.

State and persistence: creates data under a compatibility-mode WT home when requested. No latency output.

Dependencies and integration: helps test multiversion/compatibility behavior in Workgen runner scripts.

Risks: `create_compat_config` returns strings with compatibility releases that may be invalid for newer WiredTiger builds. The open config concatenates `"create,cache_size=1G,"` and the helper string that begins with a comma, producing a double comma for release cases; WT config parsing may tolerate this but it is untidy.

Test signals: workload assertions and printed records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/multiversion.py -->
