# sources/security-integrity/fscrypt/cli-tests/common.sh

## Purpose
Shared shell helpers for fscrypt CLI integration tests. It enforces execution through `run.sh`, provides failure helpers, filesystem resets, descriptor lookup, test-user execution, keyring isolation, and expect wrapping.

## APIs and Control Flow
Important helpers include `_fail`, `_expect_failure`, `_print_header`, `_reset_filesystems`, `_get_enabled_fs_count`, `_get_setup_fs_count`, `_get_protector_descriptor`, `_get_login_descriptor`, `_rm_metadata`, `_run_noisy_command`, `_user_do`, `_user_do_and_expect_failure`, `_cleanup_user_keyrings`, `_setup_session_keyring`, and an `expect` wrapper that fixes terminal width.

## State, Dependencies, and Integration
Requires `MNT`, `MNT_ROOT`, `TEST_USER`, `TMPDIR`, and `PATH` from `run.sh`. Mutates mounted test filesystems, `.fscrypt` metadata, and Linux keyrings. Uses `su`, `keyctl`, and `fscrypt status` parsing.

## Risks and Test Signals
Strict mode catches shell errors. Descriptor lookup depends on stable CLI status formatting, intentionally tying tests to user-visible output. Keyring setup re-execs the test script to obtain a clean session.
