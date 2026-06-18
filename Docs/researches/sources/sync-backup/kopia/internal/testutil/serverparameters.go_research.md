<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/serverparameters.go -->
# sources/sync-backup/kopia/internal/testutil/serverparameters.go

- Purpose: Parses ephemeral connection parameters emitted by `kopia server start`.
- Important APIs/types/functions: `serverOutputAddress`, `serverOutputCertSHA256`, `serverOutputPassword`, `serverOutputControlPassword`, `ServerParameters`, `ProcessOutput`.
- Control flow: `ProcessOutput` checks known line prefixes, fills matching struct fields, and returns false only when the server address line is seen.
- State and persistence: Stores parsed strings in a caller-owned `ServerParameters` struct.
- Dependencies and integration points: Used by tests or command runners that consume server stderr startup lines.
- Risks and edge cases: Prefix text is an implicit contract with server startup logging.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/serverparameters.go -->
