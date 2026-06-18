# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtindex.c

Formats or extends the logical Venti index mapping over configured index sections and arenas.

Key behavior:
- CLI: `fmtindex [-a] config`.
- Parses config, validates index name, counts all arenas across configured arena partitions.
- Without `-a`, creates a new index over the configured index sections.
- With `-a`, loads an existing index and appends newly configured arenas, requiring existing arena slots and addresses to match.
- Assigns index address ranges beginning at `IndexBase`, sized by arena size.
- Writes the index config/table with `wbindex`.

Interactions:
- Uses `runconfig`, `initindex`, `newindex`, and arena mappings from configured `ArenaPart`s.

Notable details:
- Fails hard on arena-order mismatch or address discontinuity in append mode.
