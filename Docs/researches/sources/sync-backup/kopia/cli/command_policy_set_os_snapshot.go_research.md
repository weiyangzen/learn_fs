<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot.go -->
# sources/sync-backup/kopia/cli/command_policy_set_os_snapshot.go

Purpose: implements OS-level snapshot policy flags, currently the Windows Volume Shadow Copy mode.

Important APIs/types/functions: `policyOSSnapshotFlags`, `setOSSnapshotPolicyFromFlags`, `applyPolicyOSSnapshotMode`, `policy.OSSnapshotMode`, and string constants `never`, `always`, `when-available`, and `inherit`.

Control flow: setup registers `--enable-volume-shadow-copy` as an enum. The setter delegates to `applyPolicyOSSnapshotMode`, where empty means unchanged, `inherit`/`default` clears the pointer, and explicit modes allocate a `policy.OSSnapshotMode` pointer.

State/persistence behavior: stores optional OS snapshot mode under `policy.OSSnapshotPolicy.VolumeShadowCopy.Enable`. Nil inherits parent/default; concrete modes override behavior.

Dependencies/integration: consumed by OS-specific snapshot support during snapshot creation and shown by policy display. Risks/test signals: mode is available in policy regardless of runtime OS; actual behavior depends on platform-specific snapshot providers elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_os_snapshot.go -->
