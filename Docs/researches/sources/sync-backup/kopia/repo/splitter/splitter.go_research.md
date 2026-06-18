# sources/sync-backup/kopia/repo/splitter/splitter.go

Purpose: defines the splitter interface, splitter size constants, registered splitter factories, and default algorithm for object chunking.

Important APIs/types/functions: `Splitter` exposes `NextSplitPoint`, `MaxSegmentSize`, `Reset`, and `Close`. `Factory` constructs splitters. `SupportedAlgorithms` returns sorted registered names. `GetFactory` fetches a factory by name. `splitterFactories` registers fixed sizes, BuzHash dynamic sizes, Rabin-Karp dynamic sizes, and legacy aliases. `DefaultAlgorithm` is `DYNAMIC-4M-BUZHASH`.

Control flow: registration is static. `SupportedAlgorithms` copies map keys and sorts them. `GetFactory` returns nil for unknown names, letting callers fall back to defaults.

State and persistence behavior: no persisted state, but chosen splitter names are stored in repository/object policy configuration and affect future content chunking/dedup behavior.

Dependencies/integration: used by object writers and snapshot splitter policy. Dynamic factories are wrapped with pooling for named modern algorithms.

Risks: changing factory names or default algorithm changes content chunking and deduplication characteristics. Legacy `DYNAMIC` maps to BuzHash instead of an old licensed implementation, so outputs differ from historical dynamic splitting.

Test signals: splitter tests verify fixed, BuzHash, Rabin-Karp, and pooled splitter stability over deterministic random data.
