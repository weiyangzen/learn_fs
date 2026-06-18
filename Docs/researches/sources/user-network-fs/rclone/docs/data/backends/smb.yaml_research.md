<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/smb.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/smb.yaml

## Purpose

`smb.yaml` is a Hugo data record describing the rclone `smb` backend as `SMB` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=smb`, `name=SMB`, `tier=Tier 2`, `maintainers=External`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Modtime`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestSMB:rclone`, `features` (10 entries), `hashes` (0 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/smb.yaml -->
