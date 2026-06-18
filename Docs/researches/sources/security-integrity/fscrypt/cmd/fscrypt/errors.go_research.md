# sources/security-integrity/fscrypt/cmd/fscrypt/errors.go

## Purpose
Centralizes CLI error values, suggestion text, and usage-error formatting.

## APIs, Types, and Control Flow
Defines user-facing errors such as cancellation, destructive operation refusal, invalid source, passphrase mismatch, missing key/protector/user, already locked/unlocked, root requirements, and keyring permissions. Struct errors cover files-open, unlocked-by-other-users, and nonempty directory cases. `suggestEnablingEncryption` emits filesystem-specific guidance for ext4 and f2fs, including kernel config, page-size limits, and GRUB warning. `getErrorSuggestions` maps action, filesystem, metadata, crypto, keyring, and command errors to actionable remediation. `newExitError` wraps errors with command name and suggestion. `usageError` prints command help before returning failure.

## State, Dependencies, and Integration
Uses filesystem inspection, kernel version helpers, `unix.Statfs`, and CLI context. It integrates tightly with command handlers through `newExitError`, `expectedArgsErr`, `onUsageError`, and `checkRequiredFlags`.

## Risks and Test Signals
Suggestions must be accurate because they can recommend destructive commands such as `tune2fs` or cache dropping. Output wrapping affects golden CLI tests. Tests indirectly cover many messages via CLI expected outputs, especially not-enabled, setup, and usage cases.
