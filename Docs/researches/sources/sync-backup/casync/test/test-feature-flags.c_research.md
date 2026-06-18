# sources/sync-backup/casync/test/test-feature-flags.c

Purpose: verifies feature flag name/string conversion and compatibility logic.

Important APIs/types/functions: iterates feature flag bits, converts to names and back, checks known/default flags, and verifies unknown or combined behavior.

Control flow/state: local arithmetic over `uint64_t` flags with assertions.

Dependencies/integration: covers `caformat-util` and `caformat` constants used to negotiate archive capabilities.

Risks/test signals: important because feature flags gate privileged metadata and compatibility. It may need updates whenever new feature bits are added.

Source research group: `subset-b-009122`.
