# sources/sync-backup/syncthing/lib/ur/contract/contract.go

Purpose: defines the JSON/database contract for anonymous usage reports and crash/failure reports.

Important APIs and control flow: `Report` contains versioned fields tagged with JSON, metric metadata, and `since` versions. It includes v1/v2/v3 usage, feature, GUI, block, transport, ignore, post-processing, and database fields. `New` allocates a report and calls `structutil.FillNil` so maps/slices are non-nil. `Validate` checks core fields and date length, and normalizes some nil slices. `ClearForVersion` recursively clears fields whose `since` tag is absent or greater than the accepted report version. `Value` marshals to JSON string for SQL driver storage. `Scan` resets the receiver before unmarshalling from `[]byte`, preventing stale fields. `FailureReport` and `FailureData` model aggregated failure uploads.

State and persistence: report values can be stored through database/sql value scanning. Clearing mutates report structs before sending/storing.

Dependencies and integration: used by `ur.Service`, failure reporting, and post-processing/metrics pipelines. Depends on reflection and `structutil`.

Risks: reflection clearing must maintain all `since` tags; missing tags zero fields. `Scan` accepts only `[]byte`, not string. Tests cover clearing and scan reset behavior.
