# sources/storage-engines/rocksdb/util/auto_tune_compressor.h

Purpose: declares auto-tuning compression components: a rejection-probability predictor for skipping unproductive compression and a cost-aware compressor scaffold for comparing CPU and I/O costs of compression levels.

Important APIs and types: `CompressionRejectionProbabilityPredictor` has `Predict`, `Record`, and `attempted_compression_count`. `AutoSkipWorkingArea` owns the wrapped compressor working area plus a shared predictor. `AutoSkipCompressorWrapper` derives from `CompressorWrapper` and overrides `Name`, clone/specialization, `CompressBlock`, `ObtainWorkingArea`, and `ReleaseWorkingArea`. `WindowAveragePredictor<T>` records window averages, with aliases `IOCostPredictor` and `CPUUtilPredictor`; `IOCPUCostPredictor` combines them. `CostAwareWorkingArea` owns a wrapped working area and a two-dimensional predictor pointer table. `CostAwareCompressor` derives directly from `Compressor`, holds compressor matrices and level indexes, and exposes dictionary, preferred type, working-area, specialization, and compression APIs. Manager classes wrap RocksDB compression manager creation.

Control flow and state: predictor state is mutable and windowed. Working-area ownership is manual: auto-skip uses `shared_ptr` for the predictor, cost-aware uses raw `IOCPUCostPredictor*` entries that the implementation deletes in `ReleaseWorkingArea`.

Dependencies and integration: depends on `rocksdb/advanced_compression.h`. The manager classes integrate with RocksDB compression option plumbing and SST creation.

Risks and test signals: the header exposes low-level ownership expectations but does not use RAII containers for cost predictors, increasing leak risk if ownership conventions change. `CostAwareCompressor` constants for exploration and cutoff are declared but the current implementation does not use them for actual choice. There are sync points in the implementation, but no local test file in this subset.
