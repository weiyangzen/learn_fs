# sources/test-tools/syzkaller/syz-cluster/pkg/db/entities.go

## Purpose
Spanner entity definitions and small domain helpers.

## Important APIs, Types, and Functions
Series, Patch, Build, Session, SessionTest, SessionTestStep, Finding, SessionReport, ReportReply, BaseFinding, SeriesStats, Job and status/helper methods.

## Control Flow
Methods set nullable fields and derive session status/duration; repositories serialize these structs.

## State and Persistence
Defines the persisted schema-facing model.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
