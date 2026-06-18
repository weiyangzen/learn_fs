# sources/sync-backup/kopia/internal/scrubber/scrub_sensitive.go

Purpose: recursively redacts struct fields marked as sensitive before logging or display.

Important APIs/types/functions: `ScrubSensitiveData(reflect.Value)`.

Control flow: expects a struct value, creates a copy, iterates fields, replaces fields tagged as sensitive with zero/redacted values, and recursively scrubs nested structs where appropriate.

State and persistence behavior: returns a scrubbed reflected value without mutating persistent storage.

Dependencies and integration points: used around config/API values that may contain secrets.

Risks and test signals: reflection can panic on unsupported inputs or unexported fields; test coverage checks nested structs, pointer-like values, and panic on non-struct input.
