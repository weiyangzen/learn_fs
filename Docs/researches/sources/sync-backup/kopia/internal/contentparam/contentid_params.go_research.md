# sources/sync-backup/kopia/internal/contentparam/contentid_params.go

Purpose: provides a content-ID-specific logging parameter that writes shortened content IDs as raw JSON.

Important APIs/types/functions: `ContentID`, private `contentIDParam`, `WriteValueTo`, and `maxLoggedContentIDLength`.

Control flow: `ContentID` captures key and `index.ID`. `WriteValueTo` allocates a fixed stack buffer, asks `index.ID.AppendToJSON` to append a JSON value capped to five content ID characters, and writes it with `RawJSONField`.

State and persistence behavior: no mutable or persistent state. The raw JSON value comes from the content index ID implementation.

Dependencies/integration: integrates `contentlog.JSONWriter` with `repo/content/index.ID`. Used by content logging benchmark and likely content operation logs.

Risks/test signals: because it uses `RawJSONField`, correctness depends on `AppendToJSON` returning valid JSON. The five-character cap deliberately trades traceability for concise logs. No direct test file is listed for this package item.
