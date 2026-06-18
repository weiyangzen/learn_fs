# sources/sync-backup/kopia/snapshot/upload/estimate.go

Purpose: estimates snapshot traversal statistics and size buckets without uploading data.

Important APIs/types/functions: `SampleBucket`, `SampleBuckets`, `makeBuckets`, `EstimateProgress`, `Estimate`, and recursive `estimate`.

Control flow: `Estimate` initializes stats and included/excluded buckets, wraps the source directory with `ignorefs.New`, records ignored entries through policy callbacks, defers final progress stats, then recursively walks entries. Directories increment total directory count, skip children when they do not support multiple iterations, report processing/progress, and account ignored or fatal directory iteration errors. Files add included bucket samples and total file counts/size.

State and persistence: no repository writes. It mutates `snapshot.Stats` atomically and reports through the progress interface.

Dependencies and integration points: used by UI/CLI estimate commands before snapshot upload; integrates policy tree ignore rules and error handling policy.

Risks and test signals: streaming directories are counted but not traversed. Directory iteration errors are reported and returned even when marked ignored. Bucket examples are capped by caller-provided max examples.
