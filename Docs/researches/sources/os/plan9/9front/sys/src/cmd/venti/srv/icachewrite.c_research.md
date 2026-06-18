# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/icachewrite.c

Background writer for dirty index-cache entries.

Key behavior:
- `initicachewrite` creates a `Round`, starts one writer proc per index section, starts a coordinator, and starts delayed kick handling.
- `icachewritecoord` waits for kicks, snapshots the newest safe arena state from `icachestate`, sends work to all index-section writers and Bloom writer, waits for completion, then advances arena tail state with `setatailstate`.
- `icachewritesect` gets dirty entries for one section range, sorts them by score, chunks nearby disk buckets into up to 8 MiB reads, updates/creates bucket entries in memory, writes the chunk back, updates any dcache-resident bucket copies, and marks entries clean.
- `nextchunk` groups dirty entries whose target bucket blocks fall within `Bufsize`.
- `iesort` merge-sorts dirty single-linked lists by score.
- Exposes `flushicache`, `kickicache`, and `delaykickicache`.

Interactions:
- Uses `disksched` to throttle writes.
- Uses `icachedirty`, `icacheclean`, `bucklook`, `packientry`, `packibucket`, and `_getdblock`.
- Coordinates Bloom write via `ix->bloom->writechan`.

Notable details:
- Bucket overflow and bad bucket paths print `XXX` diagnostics and skip affected dirty entries from that chunk.
- Flush only advances arena tail state if all section/Bloom writes succeed.
