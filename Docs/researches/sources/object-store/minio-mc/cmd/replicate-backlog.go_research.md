# Research: sources/object-store/minio-mc/cmd/replicate-backlog.go

## sources/object-store/minio-mc/cmd/replicate-backlog.go

Purpose: implements `mc replicate backlog` and alias `diff`, showing recent replication failures or full unreplicated-object diffs.

Important APIs and types: `replicateBacklogCmd`, `replicateMRFMessage`, `replicateBacklogMessage`, `replicateBacklogUI`, `keyMap`, `initReplicateBacklogUI`, `waitForActivity`, table header/style helpers, UI `Update`/`View`, and `mainReplicateBacklog`.

Control flow: the command parses bucket/prefix from the target. Without `--full`, it calls `BucketReplicationMRF` for recent failures by node; with `--full`, it calls `BucketReplicationDiff` with verbose, ARN, and prefix options. JSON mode streams each message directly. Human mode runs a Bubble Tea UI with spinner, table, key bindings, and a 10,000-row in-memory display cap.

State and persistence: read-only remote admin streams; local in-memory UI buffers rows and counts. No persistent mutations.

Dependencies and integration: uses `madmin` replication backlog APIs, Bubble Tea/Bubbles/Lipgloss terminal UI, `PrettyTable`, node color helpers, global JSON flag, and console output.

Risks and tests: `waitForActivity` reads from channels without checking closure, relying on sentinel empty records. Human UI caps displayed rows and asks JSON for full listing. No direct tests cover UI or stream closure.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/replicate-backlog.go -->
