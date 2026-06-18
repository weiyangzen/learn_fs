# sources/security-integrity/fscrypt/cli-tests/t_encrypt_login.sh

## Purpose
Tests encryption using login passphrase protectors and associated recovery behavior.

## Control Flow and Integration
Runs user encryption with `--source=pam_passphrase`, reads generated recovery passphrase, resolves recovery and login protectors, tests unlocking with login and recovery passphrases, tests interactive login encryption, tests root encrypting on behalf of a user and metadata ownership, tests `--no-recovery`, tests root-filesystem login encryption without recovery, and negative cases such as naming a login protector. Later logic also exercises linked protector status by corrupting a link UUID.

## State and Risks
Touches PAM password verification, root-mounted login protector storage, linked protectors, ownership, recovery file creation, and cross-user metadata permissions. It is sensitive to prompt output and test PAM/user setup.

## Test Signals
Provides broad coverage for the most security-sensitive login-protector workflow, including recovery passphrase integration.
