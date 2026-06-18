# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgressTypes.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/BackupProgressTypes.h

Purpose: defines the epoch metadata used by backup progress calculation.

Important type: `EpochTagsVersionsInfo`, containing tag count plus epoch begin/end versions.

Control flow and state: this is a simple value struct with an explicit constructor. It does not serialize itself here and carries no logic beyond grouping the three fields.

Dependencies and integration: depends on FDB `Version` types. `BackupProgress` consumes maps from `LogEpoch` to this struct to enumerate tags and compute unfinished backup intervals.

Risks and tests: correctness depends on callers supplying accurate tag counts and epoch boundaries. Tests should cover begin/end boundaries and changing tag counts across epochs through `BackupProgress`.
