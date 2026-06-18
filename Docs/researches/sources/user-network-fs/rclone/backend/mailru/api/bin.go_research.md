
# sources/user-network-fs/rclone/backend/mailru/api/bin.go

## Purpose
Defines constants for Mail.ru Cloud's binary protocol.

## Important APIs, Types, And Control Flow
Exports content type and fixed ID lengths, operation codes for add file, rename, create folder, folder list, shared folder list, and partially understood operations, plus result codes for mkdir, move, add-file, list options, list parse flags, list results, and directory item types.

## State And Persistence
No runtime state or persistence; all values are compile-time protocol constants.

## Dependencies And Integration Points
Consumed by Mail.ru backend request builders and binary response parsers alongside `helpers.go`.

## Risks And Test Signals
Risks are protocol drift and ambiguous TODO opcodes/result names. Tests should validate binary requests/responses against known captures and live API behavior.
