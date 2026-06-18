<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create_test.go -->
# sources/sync-backup/kopia/cli/command_repository_create_test.go

Purpose: tests repository create/connect behavior using the `from-config` provider with token files and stdin.

Important APIs/types/functions: `TestRepositoryCreateWithConfigFile`, `TestRepositoryCreateWithConfigFromStdin`, `repo.EncodeToken`, `blob.ConnectionInfo`, `filesystem.Options`, and `testenv.NewCLITest`.

Control flow: the first test checks failure messages for invalid create/connect arguments and bad tokens, writes an encoded filesystem storage token to a file, and creates the repository from `--token-file`. The second test pushes the token through runner stdin and creates with `--token-stdin`.

State/persistence behavior: creates a filesystem repository via decoded storage connection info; temp token files are written with `0600`.

Dependencies/integration: covers token decoding, storage provider registration, stdin handling, and create initialization. Risks/test signals: exact error substring assertions couple the test to provider validation wording.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repository_create_test.go -->
