# sources/sync-backup/syncthing/lib/api/support_bundle.go

Purpose: Support-bundle helpers for redacting config and writing zip archives.

Important APIs/types/functions: `getRedactedConfig` copies the service config and replaces GUI API key, password, user, and folder-device encryption passwords with `REDACTED`. `writeZip` writes `fileEntry` values to an archive.

Control flow: Redaction walks folders and embedded devices in the copied config. Zip writing creates each entry and writes its byte data, returning the first create/write error.

State and persistence behavior: `getRedactedConfig` works on a copy and does not mutate live config. `writeZip` writes to an arbitrary writer; `api.go` uses it for in-memory and backup support zips.

Dependencies and integration points: Called by `getSupportBundle` in `api.go`. Depends on config structures and the local `fileEntry` type.

Risks: Redaction covers known sensitive fields in this config shape; new secret fields require updating this helper. `writeZip` defers `Close` and also calls `Close` explicitly, which can lead to a second close on return but the explicit close result is what is returned.

Test signals: No direct tests in this subset. Support bundle endpoint tests should verify redaction and zip contents.
