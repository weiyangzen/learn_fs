# sources/sync-backup/kopia/snapshot/policy/log_detail_test.go

Purpose: verifies JSON encoding behavior for `LogDetail` values and pointers.

Important APIs/types/functions: `TestLogDetail` marshals a struct containing value and pointer `LogDetail` fields with `omitempty`, then unmarshals and compares.

Control flow: sets a pointer to `LogDetailNone`, value fields to normal and max, marshals, checks exact JSON string, then unmarshals and asserts equality.

State and persistence behavior: confirms that nil/zero value fields are omitted, while a pointer to zero is emitted as `0`; this is critical for distinguishing explicit "none" from unspecified.

Dependencies/integration: uses standard JSON and `testify/require`.

Risks: changing field pointer usage or constants can alter persisted policy JSON semantics.

Test signals: strong focused test for omitempty/pointer behavior.
