# sources/sync-backup/syncthing/cmd/syncthing/cli/errors.go

Purpose: implements CLI access to Syncthing pending GUI/system errors.

Important APIs/types/functions: `errorsCommand`, `errorsPushCommand`, `errorsPushCommand.Run`, and `errorsCommand.Run`.

Control flow: `push` posts a trimmed message to `system/error` and emits detailed status/body errors on non-200 responses. Parent `Run` dispatches `show` to `system/error` and `clear` to `system/error/clear`.

State and persistence: modifies or reads runtime error state in the running Syncthing instance via REST.

Dependencies/integration: depends on Kong selected command metadata and API helpers.

Risks and test signals: response body is included in command errors for operator diagnostics. No direct tests; relies on REST endpoint behavior.
