# `sources/user-network-fs/go-fuse/fuse/request_linux.go`

## Purpose
Linux request layout specialization.

## Important APIs, Types, And Functions
Provides Linux-specific request type definitions/aliases consumed by `parseRequest` and operation handlers.

## Control Flow
Provides Linux-specific request type definitions/aliases consumed by `parseRequest` and operation handlers.

## State And Persistence
No persistence. Risk is kernel protocol additions changing struct sizes; tests exercise Linux parsing through mounted integration and protocol server tests.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risk is kernel protocol additions changing struct sizes; tests exercise Linux parsing through mounted integration and protocol server tests.

## Test Signals
No persistence. Risk is kernel protocol additions changing struct sizes; tests exercise Linux parsing through mounted integration and protocol server tests.
