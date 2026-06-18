# sources/object-store/minio-mc/cmd/encrypt-clear.go

Purpose: Implements `mc encrypt clear` to remove bucket auto-encryption configuration.

Important APIs/types/functions: `encryptClearCmd`, `checkEncryptClearSyntax`, `encryptClearMessage`, and `mainEncryptClear`.

Control flow: Requires one target, creates a cancellable context, initializes a client, calls `DeleteEncryption`, and prints a success message.

State and persistence: Mutates remote bucket encryption configuration; no local persistence.

Dependencies/integration: Uses global context, `newClient`, client encryption API, colorjson/console, and fatal error handling.

Risks: Destructive operation has no local confirmation. All validation beyond argument count is delegated to client/server.

Test signals: No direct tests.
