# sources/sync-backup/kopia/repo/object/objectid_test.go

Purpose: verifies object ID parsing and formatting compatibility.

Important APIs/types/functions: tests cover `ParseID`, `IDsFromStrings`, `IDsToStrings`, and `ID.String`. `mustParseID` is a local helper, and `TestMain` installs the shared test harness.

Control flow: `TestParseObjectID` enumerates accepted legacy/direct/indirect/compressed strings and malformed cases. Conversion tests parse multiple IDs from strings and render them back. String tests ensure `String()` preserves exact canonical text for parsed IDs.

State and persistence behavior: no persistence is performed, but JSON/string stability is indirectly protected by canonical string expectations. The tests validate compatibility with legacy `D` direct prefixes and multiple `I` indirection prefixes.

Dependencies/integration: uses `testutil.MyTestMain` and `testify/require`. It exercises parser integration with `content/index.ParseID` through `object.ParseID`.

Risks: parser changes could silently break old manifests or object references. Invalid combinations like compressed indirect IDs must remain rejected.

Test signals: focused unit tests for syntactic compatibility; behavior of IDs in readers/writers is covered in object manager and repository tests.
