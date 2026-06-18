# sources/sync-backup/kopia/internal/server/api_estimate.go

Purpose: implements the API for estimating snapshot/upload size and exclusion statistics for a local directory.

Important APIs/types/functions: `estimateTaskProgress`, its `Processing`, `Error`, and `Stats` methods, `logBucketSamples`, and `handleEstimate`.

Control flow: decodes `EstimateRequest`, resolves and cleans the root path, verifies it is a local directory, builds a policy tree with overrides, starts an observable UI task, wires cancellation into `upload.Estimate`, reports counters and final bucket samples, then returns the task record.

State and persistence behavior: no repository mutation; task manager stores task progress/log state, and local filesystem is read.

Dependencies and integration points: integrates localfs, policy resolution, snapshot upload estimation, `uitask`, and server APIs.

Risks and test signals: only local directories are supported; request context is intentionally decoupled from cancellation by the server wrapper. Tests should cover malformed root, non-directory roots, policy override errors, cancellation, and final counters.
