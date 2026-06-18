# sources/test-tools/syzkaller/pkg/coveragedb/coveragedb_test.go

Purpose: tests coverage detail queries, especially manager-unique coverage computation, with mocked Spanner iterators.

Important APIs/types/functions: `TestFilesCoverageWithDetails`, `emptyCoverageDBFixture`, `fullCoverageDBFixture`, and `newRowIteratorMock`.

Control flow: test cases cover empty scope, empty DB with and without unique coverage, full coverage with empty partial result, exact manager/full match, and partial manager coverage. Fixture helpers build mock clients whose `Single().Query()` returns row iterators populated by `FileCoverageWithLineInfo` values.

State and persistence: in-memory mocks only.

Dependencies and integration: uses generated mocks for `SpannerClient`, `ReadOnlyTransaction`, `RowIterator`, and `Row`; imports `iterator.Done` to emulate Spanner completion.

Risks: only happy-path unique comparisons are tested; mismatch/corrupted partial-only cases are not asserted. SQL statement contents are not inspected by mocks.

Test signals: validates the subtle semantics that unique manager coverage uses full instrumentation counts but only counts lines whose manager hit count exactly accounts for all hits.
