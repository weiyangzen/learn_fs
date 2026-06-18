# sources/object-store/openstack-swift/swift/account/auditor.py

## Purpose
Defines the account database auditor daemon. It extends the common `DatabaseAuditor` to validate account DB consistency, especially totals across storage policies.

## Important APIs, Types, and Functions
`AccountAuditor` sets `server_type = "account"` and `broker_class = AccountBroker`. `_audit(info, broker)` loads policy stats with migrations enabled, sums `container_count`, `object_count`, and `bytes_used`, and returns `InvalidAccountInfo` if any total differs from `account_stat`. `main()` parses daemon options and calls `run_daemon`.

## Control Flow
The common auditor framework opens DBs and calls `_audit`. This subclass compares global account totals against `policy_stat` totals, returning an exception object on mismatch.

## State and Persistence Behavior
The auditor reads account SQLite DBs through `AccountBroker`; with `do_migrations=True`, it may trigger schema migrations for policy stats. It does not directly repair inconsistent counts beyond invoking broker migration paths.

## Dependencies and Integration Points
Depends on `AccountBroker`, `InvalidAccountInfo`, `run_daemon`, `DatabaseAuditor`, and `parse_options`. It integrates with account-server config `[account-auditor]` sections and the broader Swift daemon framework.

## Risks and Test Signals
Migrations during audit can alter DB schema, so audit runs need normal DB locking expectations. It catches aggregate-policy drift but not every per-container corruption. Test signal is auditor detection of mismatched policy totals and clean pass on valid account DBs.
