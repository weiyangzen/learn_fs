# sources/test-tools/syzkaller/syz-cluster/pkg/controller/api.go

## Purpose
Main controller HTTP server implementing api.Client routes.

## Important APIs, Types, and Functions
APIServer, NewAPIServer, Mux, and handlers for builds, findings, series, sessions, tests, artifacts, trees, base findings, test steps, and jobs.

## Control Flow
Handlers parse JSON/multipart requests, call service layer methods, map known errors to HTTP statuses, and ReplyJSON responses.

## State and Persistence
Server is stateless; services mutate Spanner rows and blob objects.

## Dependencies and Integration Points
Integrates api contracts, app environment, service layer, httptest clients, Spanner repositories, and blob storage.

## Risks and Edge Cases
Risks include incomplete request validation, inconsistent method enforcement, and broad 500 mappings for domain errors.

## Test Signals
controller/api_test.go provides full API integration coverage.
