# sources/sync-backup/syncthing/lib/config/foldertype.go

## sources/sync-backup/syncthing/lib/config/foldertype.go

Purpose: Defines configuration text forms for Syncthing folder synchronization modes.

Important APIs/types/functions: `FolderType` wraps `protocol.FolderType` values for send-receive, send-only, receive-only, and receive-encrypted. It implements `String`, `MarshalText`, and `UnmarshalText`.

Control flow and state: Legacy strings `"readwrite"` and `"readonly"` map to send-receive and send-only. Unknown values default to send-receive.

Dependencies and integration: Used by `FolderConfiguration.Type`, log attributes, metrics labels, migrations from old read-only configs, and protocol behavior.

Risks and test signals: Silent fallback to send-receive can be permissive if a config typo occurs. Historical fixtures and config tests exercise read-only/read-write migration and receive-encrypted behavior.
