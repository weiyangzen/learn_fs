# sources/sync-backup/kopia/repo/blob/sftp/sftp_storage_test.go

Purpose: integration tests for the SFTP provider against a Dockerized SSH/SFTP server and validation tests for credential path handling.

Important APIs/types/functions: helpers generate SSH keys, start `atmoz/sftp`, wait for a TCP banner, scan host keys, create SFTP storage with optional embedded credentials, clear blobs, and read credential files. Tests are `TestSFTPStorageValid`, `TestInvalidServerFailsFast`, `TestSFTPStorageRelativeKeyFile`, and `TestSFTPStorageRelativeKnownHostsFile`.

Control flow: the main test starts a container with one key-auth and one password-auth user, opens storage with a context that is canceled after construction, clears any blobs, runs the standard blob storage contract suite and provider validation, asserts connection-info round trips, and closes. It repeats with key material and known-hosts data embedded in options, then tests password auth.

State and persistence behavior: remote data lives under `/upload` or `/upload2` in the container and is deleted before and after validation. Temporary local credential directories and known-host files are cleaned by test cleanup handlers.

Dependencies/integration: requires Docker, `ssh-keygen`, `ssh-keyscan`, Linux/amd64 CI allowance, blobtesting, provider-validation, and the SFTP provider itself.

Risks and edge cases: container startup and key scanning are timing-sensitive. Invalid-host fast failure guards against reconnect/retry loops. Relative-path tests protect against unsafe config serialization and working-directory-dependent credentials.

Test signals: success confirms SFTP satisfies the shared blob contract under key/password auth, supports embedded connection info, rejects unsafe relative paths, and fails quickly on unreachable servers.
