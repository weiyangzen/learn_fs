# sources/user-network-fs/samba/source4/torture/drs/python/samba_tool_drs_showrepl.py

## Purpose
`samba_tool_drs_showrepl.py` is a blackbox suite for `samba-tool drs showrepl`. It validates human-readable output, JSON output, all-good pull-summary output including color behavior, and failure summary output when replication is deliberately disabled.

## Important APIs, Types, And Functions
- `SambaToolDrsShowReplTests` extends `drs_base.DrsBaseTestCase`.
- Regex constants describe GUID, hex option, and DN formats expected in command output.
- `_force_all_reps()` uses `drs_utils.drsuapi_connect()`, `DsReplicaGetInfo`, LDAP searches, and `_net_drs_replicate()` to force inbound or outbound replication with non-RODC live partners.
- Tests use `json`, `os.environ["NO_COLOR"]`, and `BlackboxProcessError` inspection.

## Control Flow
The text-output test runs KCC, forces bidirectional replication for config/domain/schema NCs, runs `showrepl`, splits output into header/inbound/outbound/KCC sections, and matches each section with regexes. The JSON test parses `--json` output and validates top-level keys and value types. The all-good summary test enables replication, forces all neighbor replication, then checks `--pull-summary` with plain, verbose, color yes/always/never/auto, and `NO_COLOR` combinations. The failure test disables replication on DC1, creates many unreplicated users under DC-specific OUs, repeatedly calls `--summary -v` until the command fails, and checks the failure report.

## State And Persistence Behavior
The suite mutates replication topology by running KCC, enabling/disabling replication, and creating temporary OUs/users. Cleanup callbacks remove created OUs and re-enable replication. It temporarily modifies `NO_COLOR` and restores it in `finally`.

## Dependencies And Integration Points
This integrates CLI showrepl formatting, DRS replica-info RPC, LDAP inspection of NTDS Settings/server objects, KCC connection objects, replication status counters, ANSI color policy, and summary failure detection. It also filters RODCs and deleted DCs in `_force_all_reps()`.

## Risks
Output-format tests are intentionally brittle and will fail on legitimate formatting changes. DN regexes are domain-shape-specific (`DC=com`), which may limit portability. The forced-failure test loops up to 100 changes and relies on replication status noticing disabled replication in time. Environment color behavior can vary if terminal detection changes.

## Test Signals
Signals include exact section headers, header GUID/option regex matches, inbound/outbound neighbor blocks for config/domain/schema NCs, KCC connection object details, JSON keys `repsFrom`, `repsTo`, `NTDSConnections`, and `dsa`, type/regex validation for JSON fields, `[ALL GOOD]` with or without ANSI green according to color settings, and forced failure output containing `There are failing connections`, `WERR_DS_DRA_SINK_DISABLED` or `WERR_DS_DRA_SOURCE_DISABLED`, and `consecutive failure(s).`
