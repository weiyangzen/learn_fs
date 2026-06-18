# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_realos_other.go

Purpose: default non-Unix implementation of stale-file-handle detection for `realOS`.

Important APIs/types/functions: `realOS.IsStale`.

Control flow: on platforms without Unix `ESTALE` handling, the method returns false, so stale-specific retry suppression does not apply.

State and persistence behavior: none; it only classifies errors.

Dependencies/integration points: selected by build tags and consumed by `fsImpl.isRetriable`. Risks include a platform that can produce stale-handle-like errors but is covered by this fallback, causing retry classification differences. Test signals are indirect on non-Unix builds.
