# sources/user-network-fs/rclone/backend/union/policy/epmfs.go

Purpose: existing-path most-free-space policy.

Important APIs: `EpMfs`, registered as `epmfs`; helpers `mfs` and `mfsEntries`.

Control flow/state: after existing-path filtering, chooses the candidate with largest free-space metric.

Dependencies/integration: `context`, `upstream`, `fs`; used by the default create policy family through `Mfs`.

Risks/test signals: unsupported free space may look extremely large, causing skewed selection; usage cache can lag writes. Generic union tests cover default policy behavior.
