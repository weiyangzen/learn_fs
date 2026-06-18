# sources/sync-backup/borg/src/borg/testsuite/helpers/passphrase_test.py

Purpose: tests passphrase prompting, display/debug controls, retry behavior, empty-passphrase rejection, and secret-safe representations.

Important APIs and control flow: `Passphrase.new` is tested with monkeypatched `getpass.getpass`, `BORG_DISPLAY_PASSPHRASE` on/off, non-ASCII passphrases, printable special characters, empty input, and repeated mismatches causing `PasswordRetriesExceeded`. `repr(Passphrase)` must not reveal the secret. `display_debug_info` only prints wrong passphrase and related environment variables when `BORG_DEBUG_PASSPHRASE=YES`. `verification` prints plaintext and hex only when display is enabled.

State and persistence: mutates environment variables and captures stderr/stdout with pytest. No secrets are written to disk.

Dependencies and integration points: depends on `helpers.passphrase.Passphrase`, `PasswordRetriesExceeded`, `getpass`, and hex conversion. It integrates with key creation/detection and CLI safety.

Risks: tests deliberately check for absence of secrets in normal output. Debug modes intentionally leak passphrases when enabled, so gating must remain strict.

Test signals: captured output contains or omits passphrase/hex text as expected, retries fail with the right exception, and `repr` redacts.
