# sources/test-tools/pynfs/nfs4.1/server41tests/st_trunking.py

Purpose: basic multi-session-per-client tests used as a starting point for trunking/session-lifetime coverage.

Important APIs/types/functions: `testTwoSessions` and `testUseTwoSessions`.

Control flow: `testTwoSessions` creates one client and two sessions. `testUseTwoSessions` creates two sessions, sends empty compounds on both, destroys the first session via `DESTROY_SESSION`, then verifies the second session remains usable.

State and persistence behavior: mutates client session state on the server but no filesystem data. It specifically checks that session destruction is scoped to the target session and not the whole clientid.

Dependencies/integration: uses `NFS4ops.destroy_session`, `nfs4lib`, generated types, and environment client/session factories.

Risks and test signals: imports `random` and `threading` are unused. Comments outline many unimplemented trunking/callback scenarios, so current coverage is intentionally shallow.
