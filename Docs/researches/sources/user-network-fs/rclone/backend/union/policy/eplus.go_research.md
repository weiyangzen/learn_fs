# sources/user-network-fs/rclone/backend/union/policy/eplus.go

Purpose: existing-path least-used-space policy.

Important APIs: `EpLus`, registered as `eplus`; helpers `lus` and `lusEntries`; category methods.

Control flow/state: uses `EpAll` to filter candidates, then selects the smallest `GetUsedSpace` value.

Dependencies/integration: `context`, `math`, `upstream`, `fs`; concrete `Lus` overrides create behavior while reusing helpers.

Risks/test signals: unsupported or stale usage data can skew placement. `TestPolicy1` exercises `lus` as create policy at contract level.
