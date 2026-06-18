# sources/storage-engines/foundationdb/fdbcli/ConsistencyScanCommand.cpp

Purpose: Implements `consistencyscan`, which reads or changes configuration for the Consistency Scan role and exposes current/lifetime scan statistics.

Important APIs/types/functions: `consistencyScanCommandActor(Database, tokens)`, `dumpStats`, `ConsistencyScanState`, `ConsistencyScanState::Config`, `ReadYourWritesTransaction`, `SystemDBWriteLockedNow`, and options `on`, `off`, `restart`, `stats`, `clearstats`, `maxRate`, and `targetInterval`.

Control flow: Tokens after the command are placed in a list. The command creates a RYW transaction, applies system DB write-lock options, reads scan config, and either prints JSON when no args are supplied or walks arguments sequentially. Boolean toggles mutate `config.enabled`; `restart` sets `minStartVersion` from the transaction read version; `stats` prints current/lifetime JSON stats; `clearstats` clears stats; numeric options parse the next argument with `boost::lexical_cast<int>`. The updated config is written and committed with normal `onError` retry.

State and persistence behavior: Configuration and stats live in system metadata managed by `ConsistencyScanState`. The command mutates persisted config/stats; output is JSON generated from current state.

Dependencies and integration points: Depends on fdbclient consistency-scan state abstractions, RYW transaction semantics, system database lock-aware options, JSON serialization, and status JSON conventions documented in the help text.

Risks: Invalid numeric conversions are not explicitly caught by this actor, so lexical-cast exceptions may escape rather than becoming clean usage output. `tokens[2]` is not accessed directly, but option parsing accepts unknown trailing tokens silently if they are not matched and do not set `error`, so tests should pin intended behavior. Stats operations and config writes share one transaction.

Test signals: Exercise no-arg JSON, enable/disable, restart version update, stats and clearstats, numeric options, missing numeric values, retry on transaction errors, and unknown-token behavior.
