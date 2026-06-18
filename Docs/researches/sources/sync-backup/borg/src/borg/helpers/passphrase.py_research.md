# sources/sync-backup/borg/src/borg/helpers/passphrase.py

## Purpose
Acquires, validates, and displays encryption passphrases from environment variables, commands, file descriptors, and interactive prompts while hiding values in repr output.

## Important APIs, Types, And Functions
Error classes: `NoPassphraseFailure`, `PasscommandFailure`, `PassphraseWrong`, and `PasswordRetriesExceeded`. `Passphrase` subclasses `str` and provides `_check_ambiguity`, `_env_passphrase`, `env_passphrase`, `env_passcommand`, `fd_passphrase`, `env_new_passphrase`, `getpass`, `verification`, `display_debug_info`, `new`, and redacted `__repr__`.

## Control Flow
`env_passphrase` rejects ambiguous simultaneous sources, then tries direct env var, passcommand, and fd in order. `env_passcommand` runs a shell-split command with sanitized system environment and strips one trailing newline. `fd_passphrase` reads all text from a numeric fd. `new` prefers new-passphrase env, then existing passphrase sources, then prompts up to ten times with confirmation and optional display verification.

## State And Persistence
Passphrases are plain Python strings in memory. The module reads environment variables and may consume/close the fd named by `BORG_PASSPHRASE_FD`. It does not persist secrets, but debug/verification paths can print them intentionally.

## Dependencies And Integration Points
Depends on `yes`, `prepare_subprocess_env`, Borg error classes, hex formatting, logger, `getpass`, `subprocess`, and command-line encryption/key handling. Supports primary and `other` repository passphrase namespaces.

## Risks And Edge Cases
Environment ambiguity is fatal. `BORG_DEBUG_PASSPHRASE=YES` and verification can reveal secrets on stderr by design. `shlex.split` means passcommands are not shell-expanded. FD reads close the descriptor. Interactive failure reports which passphrase env vars are set. Empty passphrases are rejected by `new` unless allowed.

## Test Signals
Existing passphrase tests should cover source precedence, ambiguity, passcommand success/failure, fd reading, EOF handling, retry exhaustion, empty-passphrase policy, debug output gating, verification prompt env override, and redacted repr.
