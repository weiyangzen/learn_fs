# sources/test-tools/syzkaller/pkg/email/lore/parse_test.go

Purpose: `lore/parse_test.go` exercises thread extraction, patch subject parsing, discussion classification, patch-series construction, and lore URL formatting.

Important tests: `TestThreadsCollection` builds root/reply/orphan/own-email scenarios and validates resulting threads, bug IDs, and message ordering. `TestParsePatchSubject` checks plain, cover, numbered, RFC, versioned, resend, and net-next subjects. `TestDiscussionType` checks patch, reminder, report, and mention classification. `TestParseSeries` verifies single patches, cover-letter series, missing patches marked corrupted, and reply subjects without patches. `TestLink` validates message and thread URL helpers.

Control flow and state: tests parse raw email strings through `lore.Parse`, then normalize fields not relevant to grouping before comparing deep structures. Series tests use a dummy diff to set `HasPatch`.

Dependencies and integration: the test crosses `pkg/email` parsing, patch extraction, bug ID extraction, and dashboard discussion type constants.

Risks/test gaps: tests do not cover all malformed subject forms or duplicate patch sequence handling. They also do not verify base-commit propagation in series despite code support. Coverage is nevertheless strong for the primary lore grouping semantics.
