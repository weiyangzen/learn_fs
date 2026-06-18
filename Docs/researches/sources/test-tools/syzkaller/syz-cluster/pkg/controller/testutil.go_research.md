# sources/test-tools/syzkaller/syz-cluster/pkg/controller/testutil.go

## Purpose
Shared controller/reporter/retest test helpers.

## Important APIs, Types, and Functions
UploadTestSeries, UploadTestBuild, TestServer, DummySeries, DummyBuild, DummyFindings, FakeSeriesWithFindings, StartSession, MarkSessionFinished, UploadTestSessionReport, FakeJobSession.

## Control Flow
Composes public API calls and direct repository mutations for setup shortcuts.

## State and Persistence
Creates transient Spanner records and httptest servers.

## Dependencies and Integration Points
Integrates api contracts, app environment, service layer, httptest clients, Spanner repositories, and blob storage.

## Risks and Edge Cases
Risks include incomplete request validation, inconsistent method enforcement, and broad 500 mappings for domain errors.

## Test Signals
controller/api_test.go provides full API integration coverage.
