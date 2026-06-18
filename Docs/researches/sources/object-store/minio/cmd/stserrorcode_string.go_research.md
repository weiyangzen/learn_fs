# sources/object-store/minio/cmd/stserrorcode_string.go

Purpose: generated `stringer` output for the `STSErrorCode` enum declared in `sts-errors.go`. It converts STS error constants into stable symbolic strings such as `STSAccessDenied`, `STSMissingParameter`, `STSInvalidParameterValue`, and `STSInternalError`.

Important APIs and functions: the only runtime API is `(STSErrorCode).String() string`. The sentinel `_()` function uses compile-time array indexes to fail the build if enum numeric values move without regenerating this file. `_STSErrorCode_name` is a packed string table and `_STSErrorCode_index` stores offsets into it.

Control flow: `String` bounds-checks the integer enum value. Known values return a substring from the packed table; unknown or negative values return `STSErrorCode(<n>)` using `strconv.FormatInt`.

State and persistence: there is no mutable state or persistence. The file is deterministic generated code and should be regenerated, not manually edited, when STS error constants change.

Dependencies and integration points: depends only on `strconv` and the `STSErrorCode` constants in the same package. It is used wherever MinIO logs, serializes, or tests STS error-code names.

Risks: the main risk is stale generated output after editing `sts-errors.go`. The compile-time checks catch numeric changes, but not semantic renames if the enum order stays compatible. Because STS errors are externally visible through APIs/logs, accidental renames can affect diagnostics and tests.

Test signals: no dedicated test in this file. Build success is the primary generated-code signal; any code path comparing `STSErrorCode.String()` output indirectly exercises it.
