# sources/sync-backup/kopia/internal/ospath/ospath_openbsd.go

Purpose: OpenBSD-specific path initialization.

Important APIs/types/functions: `init` sets OpenBSD config/log defaults.

Control flow: package initialization assigns OS-appropriate directories.

State and persistence behavior: process-global directory variables only.

Dependencies and integration points: consumed through `ConfigDir` and `LogsDir`.

Risks and test signals: platform-specific default paths should be checked in OpenBSD CI or targeted unit tests.
