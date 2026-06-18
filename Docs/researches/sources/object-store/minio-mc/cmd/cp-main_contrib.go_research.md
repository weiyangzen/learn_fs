# sources/object-store/minio-mc/cmd/cp-main_contrib.go

Purpose: Parses `mc cp --attr` custom metadata strings into canonical HTTP metadata keys and values.

Important APIs/types/functions: `getMetaDataEntry` and `ErrInvalidMetadata` from `cp-main.go`.

Control flow: A small rune parser alternates between key and value tokens, with normal, single-quoted, and double-quoted states. Unquoted `=` separates key/value, unquoted `;` separates entries, and delimiters inside quotes are preserved. EOF validates that the parser is in value state and not inside a quote, then emits the final entry.

State and persistence: Stateless parsing only.

Dependencies/integration: Uses `http.CanonicalHeaderKey` and probe errors. Called by copy transfer setup to populate `TargetContent.UserMetadata`.

Risks: Empty keys/values are not deeply validated beyond parser state. Parser panics on impossible internal states. Quoting support is custom and must remain compatible with shell quoting expectations.

Test signals: `cp-main_test.go` covers multiple delimiters, repeated `=`, quoted semicolons, quoted keys, and unterminated quotes.
