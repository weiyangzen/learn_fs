# sources/object-store/minio/cmd/erasure-healing-common.go

Purpose: Provides common metadata-reduction and part-verification helpers used to decide which disks are online, current, stale, corrupt, or missing before object healing rewrites data.

Important APIs/types/functions: `commonETags`, `commonTimeAndOccurrence`, `commonTime`, and `commonETag` choose quorum-common metadata values. `timeSentinel`/`timeSentinel1970` represent missing/legacy timestamps. `listObjectETags` and `listObjectModtimes` extract per-disk metadata signals. `listOnlineDisks` selects disks whose `FileInfo` matches quorum modtime or ETag fallback. `convPartErrToInt`, `partNeedsHealing`, and `countPartNotSuccess` normalize part-check states. `checkObjectWithAllParts` validates metadata consistency, erasure distribution reliability, inline data bitrot, and per-part presence/checksums via `CheckParts` or `VerifyFile`.

Control flow and state: `checkObjectWithAllParts` first detects unreliable erasure distributions, filters stale/corrupt metadata from `onlineDisks`, maps metadata errors into all part results, then verifies each disk’s data or inline data. It returns two maps: errors by disk and errors by part. It mutates the supplied `onlineDisks` and `partsMetadata` slices in place to remove unusable entries.

Dependencies and integration points: Depends on `FileInfo`, `StorageAPI`, bitrot verification, `madmin.HealScanMode`, storage `CheckParts`/`VerifyFile`, and check-part constants. `healObject` consumes its outputs to decide repair targets and dangling status.

Risks: In-place mutation is intentional but easy to misuse if callers expect original metadata. The ETag fallback can select a quorum when modtimes are missing, but only if common version quorum exists. Distribution reliability heuristics must avoid both false healing and false corruption under manually altered backends.

Test signals: Common tests cover quorum time selection, online disk filtering, small and regular object verification, corrupt/missing parts, and parity selection behavior.
