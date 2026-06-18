# sources/test-tools/syzkaller/syz-cluster/pkg/controller/api_test.go

## Purpose
End-to-end controller API integration tests.

## Important APIs, Types, and Functions
Tests cover series/build/finding/artifact/base-finding/previous-finding/test-step/tree/job/session-info flows.

## Control Flow
Uses app.TestEnvironment, httptest controller, public api.Client calls, and direct db checks where needed.

## State and Persistence
Exercises transient Spanner plus local blob storage across most core entities.

## Dependencies and Integration Points
Integrates api contracts, app environment, service layer, httptest clients, Spanner repositories, and blob storage.

## Risks and Edge Cases
Risks include incomplete request validation, inconsistent method enforcement, and broad 500 mappings for domain errors.

## Test Signals
controller/api_test.go provides full API integration coverage.
