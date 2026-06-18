<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure.go -->
# sources/user-network-fs/rclone/fs/config/obscure/obscure.go

## Purpose
Implements rclone's reversible password/value obscuring format. It is intended to prevent casual inspection in config files, not to provide strong secret storage.

## Important APIs, Types, And Control Flow
`Obscure` prepends a random AES block-size IV, encrypts plaintext with AES-CTR using a package static key, and encodes with raw URL-safe base64. `Reveal` decodes, validates minimum length, splits IV and ciphertext, and applies the same CTR operation in place. `MustObscure` and `MustReveal` fatal-log on failure.

## State And Persistence
Package globals hold the static key, lazily initialized AES block, and `cryptRand` reader. Obscured strings are stored by config callers; this file itself persists nothing.

## Dependencies And Integration Points
Uses Go crypto AES/CTR, crypto random, raw URL base64, and `fs.Fatalf`. Config UI and remote update/password paths call these helpers for password options.

## Risks And Test Signals
Because the key is embedded in source, obscuring is reversible by anyone with rclone. In-place reveal mutates the decoded buffer but not caller input. Tests pin deterministic IV outputs, bidirectionality, and decode/short-input errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config/obscure/obscure.go -->
