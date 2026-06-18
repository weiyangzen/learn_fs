# sources/sync-backup/kopia/internal/ospath/ospath_darwin.go

Purpose: Darwin-specific path initialization.

Important APIs/types/functions: `init` sets config and log directory defaults under macOS user library locations.

Control flow: runs at package initialization after shared variables are available.

State and persistence behavior: updates process-global path variables only.

Dependencies and integration points: affects `ConfigDir` and `LogsDir` on macOS.

Risks and test signals: macOS directory conventions should be verified in platform tests, especially when home directory discovery fails.
