# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dns.h

Shared header for the Plan 9 DNS/NDB stack. It defines DNS protocol constants, RR type IDs, class/opcode/rcode/flag values, timing constants, payload limits, hash sizes, request timeouts, parallelism limits, and magic numbers.

Core data structures include `Request`, `Querylck`, `DN`, `RR`, DNSSEC-adjacent payload structs (`Key`, `Cert`, `Sig`, `Null`), `Txt`, `Server`, `SOA`, `Srv`, `DNSmsg`, `Area`, `Cfg`, and `Stats`. `RR` is a compact tagged structure using unions keyed by type/negative state.

The header declares globals shared across daemon, resolver, database, server, notify, and transport files: cache config, mount point, time bases, area lists, stats, debug flags, and zone refresh state. It also declares all cross-module functions for cache management, DB lookup, server dispatch, conversion, notify, resolver transport, and logging.

Important design signal: ownership of RR lists is manual and lock-sensitive. Many APIs return copied lists or transfer ownership; callers frequently free with `rrfreelist()` under `dnlock` depending on cached/shared status.

Risks include broad global coupling and typo-preserved protocol names such as `Runimplimented`. The header is the central contract; changing struct layout or enum values affects packet conversion, cache comparison, formatting, and all server paths.
