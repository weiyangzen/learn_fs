# sources/storage-engines/badger/badger/cmd/info.go

Purpose: implements `badger info`, a health and inspection command for manifests, value logs, SSTables, keys, histograms, and discard stats.

Important APIs and flow: flags control table display, histogram, key listing, prefix filter, lookup, metadata, history, internal keys, read-only/truncate, encryption key, checksum verification mode, discard-file parsing, and external magic. `handleInfo` builds Badger options, optionally prints discard stats, calls `printInfo` to replay the manifest and compare disk files, opens the DB, and conditionally calls table, histogram, key listing, and lookup routines. `printInfo` reports manifest truncation, missing/extra/empty files, value-log size, level sizes, and abnormalities.

State and persistence: usually read-only, but `--read-only=false` and truncate options can allow recovery-style opens. Dependencies are Badger manifest/table APIs, filesystem walking, hex decoding, humanize, and options checksum enums. Risks: `checksumVerificationMode` accepts `"tableAndblock"` but flag help says `tableAndBlock`; invalid mode calls `os.Exit(1)` instead of returning an error; mean compression ratio divides by table count. Test signals should cover manifest replay, key lookup/history, prefix decoding failures, discard stats, and abnormal file reporting.
