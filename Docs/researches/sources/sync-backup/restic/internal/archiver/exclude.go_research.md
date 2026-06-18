# sources/sync-backup/restic/internal/archiver/exclude.go

Purpose: Implements archiver exclusion predicates for tag files, device boundaries, file size, and online-only cloud files. It adapts user-facing backup options into `SelectByNameFunc` and `SelectFunc` style predicates.

Important APIs and types: `RejectByNameFunc`, `RejectFunc`, `CombineRejectByNames`, and `CombineRejects` convert reject predicates into positive select functions. `RejectIfPresent` parses `filename[:header]` tag-file specs and returns a cached predicate. `RejectByDevice` builds a `deviceMap` for `--one-file-system`; `RejectBySize` rejects files larger than a maximum; `RejectCloudFiles` rejects files whose metadata reports recall-on-data-access. Internal helpers include `rejectionCache`, `isExcludedByFile`, `isDirExcludedByFile`, `newDeviceMap`, and `deviceMap.IsAllowed`.

Control flow and state: Tag-file rejection checks the containing directory, caches the decision by directory, avoids excluding the tag file itself, and optionally validates a required header. Device rejection normalizes sample paths, maps allowed source roots to device IDs, walks parent directories to find the controlling allowed device, rejects files on other devices, and specially keeps mountpoint directories when their parent is allowed. Size and cloud predicates are stateless.

Persistence and dependencies: This code reads filesystem metadata and tag-file content through `internal/fs.FS`; it does not persist data. It depends on `debug`, `errors`, runtime OS checks, and `fs.ExtendedFileInfo` methods such as `RecallOnDataAccess`.

Integration points: These predicates feed archiver and scanner selection. `RejectIfPresent` supports cache-directory and user tag-file exclusions; `RejectByDevice` enforces filesystem boundary behavior; `RejectCloudFiles` protects against hydrating online-only files.

Risks and test signals: Important risks are stale cache decisions if tag files change during traversal, warning-only handling for malformed tag files, panics if `deviceMap.IsAllowed` unexpectedly cannot locate an ancestor, Windows lack of device IDs, and mountpoint directory inclusion semantics. `exclude_test.go` covers tag signatures, multiple tag rules, size rejection, and device-map boundary decisions.
