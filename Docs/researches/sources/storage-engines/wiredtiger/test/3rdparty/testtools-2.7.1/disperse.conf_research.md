# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/disperse.conf

Purpose: release automation configuration for the `disperse` tool.

Important APIs, types, and functions: YAML-like keys set `timeout_days: 5`, `tag_name: "$VERSION"`, and `launchpad_project: "testtools"`.

Control flow: disperse reads the file during release orchestration, waits up to the configured timeout, tags with the resolved version string, and targets the Launchpad project.

State and persistence: no runtime state in this repo file. Disperse may create tags or remote release state when used.

Dependencies and integration points: depends on the external `disperse` tool and Launchpad project naming.

Risks and test signals: release-side effects are remote and version-sensitive. Test signal is dry-run or controlled release tooling recognizing the configuration.
