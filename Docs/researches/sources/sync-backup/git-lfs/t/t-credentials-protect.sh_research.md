# sources/sync-backup/git-lfs/t/t-credentials-protect.sh

## Purpose
Security tests for credential protocol protection against control characters embedded in credential fields, especially URL paths decoded from `%0a`, `%0d`, and `%00`.

## Important APIs, Functions, and Control Flow
`setup_creds` prepares credential records and copies localhost credentials. Each test creates an LFS object, configures `lfs.url` to a localhost URL whose repository path contains an encoded line feed, carriage return, or null byte, creates the matching remote directory, attempts `git lfs push`, and inspects credential rejection. The carriage-return case also disables `credential.protectProtocol` and expects success; newline and null remain rejected.

## State, Persistence, and Dependencies
State includes `CREDSDIR`, local config `lfs.url`, optional `credential.protectProtocol`, server repositories with encoded names, and server object store. Dependencies include `setup_creds`, `setup_remote_repo`, `refute_server_object`, and `assert_server_object`.

## Integration Points, Risks, and Test Signals
Integration is with Git credential protocol serialization and LFS endpoint URL parsing. Signals are `credential value for path contains newline/carriage return/null byte`, missing credential errors, success after disabling protection for carriage return, and object-store assertions. Risks are URL-decoding differences and exact security error text.
