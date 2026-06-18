# sources/user-network-fs/rclone/backend/dropbox/dropbox_internal_test.go

Purpose: This file contains Dropbox-specific internal tests beyond the generic rclone integration suite. It validates filename length prechecks and the special Dropbox Paper export path.

Important APIs and types: The tests call `checkPathLength`, use `maxFileNameLength`, call `Fs.importPaperForTest`, `Fs.InternalTestPaperExport`, and expose `Fs.InternalTest` through `fstests.InternalTester`. The Paper test uses Dropbox SDK `files.PaperCreateArg` and `ImportFormatMarkdown`, plus rclone object lookup/open APIs.

Control flow: `TestInternalCheckPathLength` builds repeated rune strings for ASCII, pound sign, smiley, and CJK characters, both as whole names and path components, then asserts that lengths up to 255 pass and 256 fail. `importPaperForTest` creates a Paper document under the remote root from markdown content. `InternalTestPaperExport` changes preferred export extension to HTML, resolves `export.html`, opens it, reads the content, and checks expected rendered HTML fragments. `InternalTest` registers that subtest for the generic test harness.

State and persistence behavior: The path-length test is pure. The Paper test creates a real Dropbox Paper document in the integration remote and reads it back through the export path, mutating remote test state.

Dependencies and integration points: It integrates Dropbox Paper creation with rclone's export metadata mapping and `fstests.InternalTester`. It depends on the backend's pacer and SDK client being configured by the integration harness.

Risks: Paper tests require a Dropbox account and API behavior that supports Paper creation/export. The content assertions are intentionally small and may be sensitive to Dropbox export formatting changes. `checkPathLength` test asserts the backend's rune-count approximation, not Dropbox's exact server-side length metric.

Test signals: Strong signals are exact pass/fail path length cases and successful Paper import, lookup as `export.html`, readable object stream, and rendered snippets including bold text and link markup.
