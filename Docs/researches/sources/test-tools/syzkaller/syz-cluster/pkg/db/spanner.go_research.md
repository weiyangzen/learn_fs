# sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner.go

## Purpose
Spanner setup, migration, test-emulator, query, and generic repository helpers.

## Important APIs, Types, and Functions
ParseURI, CreateSpannerInstance, CreateSpannerDB, RunMigrations, NewTransientDB, NewTestDB, readEntity/readEntities, addLimit, genericEntityOps.

## Control Flow
Production runs embedded migrations; tests start emulator and isolated DBs; generic ops wrap insert/update/upsert/get.

## State and Persistence
Manages Spanner DBs and helper access to persisted rows.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.
