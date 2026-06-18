# sources/sync-backup/kopia/repo/maintenancestats/builder.go

Purpose: serializes and deserializes typed maintenance stats into generic schedule extras.

Important APIs/types/functions: `Extra`, `Summarizer`, `Kind`, `ErrUnSupportedStatKindError`, `BuildExtra`, and `BuildFromExtra`.

Control flow: `BuildExtra` validates non-nil stats, marshals the struct to JSON, and stores its kind string. `BuildFromExtra` switches on kind, allocates the matching stats struct, unmarshals raw JSON into it, and returns it as a `Summarizer`.

State/persistence behavior: `Extra` values are persisted in maintenance schedule `RunInfo.Extra`, preserving task-specific stats without coupling schedule schema to each struct.

Dependencies/integration: used by `maintenance.buildRunStats` and task stats files.

Risks/test signals: every new stats kind must be registered in the switch or stored extras become unsupported. Tests cover success and error cases for all known kinds.
