# sources/sync-backup/kopia/internal/scrubber/scrub_sensitive_test.go

Purpose: tests sensitive-field redaction.

Important APIs/types/functions: test structs `S` and `Q`, `TestScrubber`, and `TestScrubberPanicsOnNonStruct`.

Control flow: builds structs with sensitive tags, scrubs them, and compares output; separately asserts non-struct input panics.

State and persistence behavior: no persistence.

Dependencies and integration points: validates the reflection contract for callers that log scrubbed values.

Risks and test signals: should be expanded when new tag conventions or nested container types are supported.
