# sources/sync-backup/kopia/internal/repotesting/repotesting_test.go

Purpose: validates that repository test environments wire custom time functions into repository operations.

Important APIs/types/functions: `TestTimeFuncWiring`.

Control flow: creates a test environment with fake time options and verifies repository behavior observes that time source.

State and persistence behavior: temporary repository state only.

Dependencies and integration points: protects consumers relying on deterministic timestamps in tests.

Risks and test signals: narrow coverage; most `repotesting` behavior is tested indirectly by broad repository/server tests.
