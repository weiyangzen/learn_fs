# sources/sync-backup/kopia/tests/end_to_end_test/policy_test.go

## Purpose
Tests default global policy creation and visibility in content, manifest, and policy listing commands.

## Important APIs, Types, and Functions
`TestDefaultGlobalPolicy` uses `content.Info`, `manifest.EntryMetadata`, and `policy.TargetWithPolicy`.

## Control Flow
The test creates a repo, shows global policy, parses `content ls --json` and expects one content item, shows that content, parses manifest list filtered to global policy and expects one entry, then parses policy list and expects one policy.

## State and Persistence Behavior
Repository creation persists the default global policy as content and manifest metadata.

## Dependencies and Integration Points
Exercises repo initialization, policy show/list, content list/show, manifest list filters, and JSON output parsing.

## Risks
Assumes repository creation writes exactly one content item before any other side effects. Additional default metadata would require test updates.

## Test Signals
Confirms default global policy is stored and discoverable through all relevant CLI surfaces.
