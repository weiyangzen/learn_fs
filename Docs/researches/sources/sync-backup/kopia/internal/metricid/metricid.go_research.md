# sources/sync-backup/kopia/internal/metricid/metricid.go

Purpose: defines stable numeric IDs for well-known Kopia metric names so snapshots can be serialized compactly.

Important APIs/types/functions: global mappings `Counters`, `DurationDistributions`, and `SizeDistributions`, all created with `NewMapping`.

Control flow: package initialization builds mappings from literal metric-name maps. Counter IDs cover blob, content compression, encryption, hashing, read/write, and upload/download metrics. Duration distribution IDs cover blob storage latency by method. Size distribution mapping is currently empty but reserved.

State/persistence behavior: these numeric IDs are persistent compatibility state; comments require adding new items with consecutive values. Reordering or renumbering existing entries would break compact historical metric decoding.

Dependencies/integration: consumed by metric snapshot serialization/deserialization paths outside this subset. Names include label suffixes such as `[method:GetBlob-full]`.

Risks/test signals: manual maintenance is required when adding metrics. Empty `SizeDistributions` is valid but means no compact IDs are currently assigned for size distributions.
