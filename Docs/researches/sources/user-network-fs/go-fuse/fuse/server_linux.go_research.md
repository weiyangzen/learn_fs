# `sources/user-network-fs/go-fuse/fuse/server_linux.go`

## Purpose
Linux server response writer and splice policy.

## Important APIs, Types, And Functions
Defines `useSingleReader=false` and `Server.write`; writes header-only replies with writev, optionally splices fd-backed reads, otherwise materializes bytes and reserializes lengths.

## Control Flow
Defines `useSingleReader=false` and `Server.write`; writes header-only replies with writev, optionally splices fd-backed reads, otherwise materializes bytes and reserializes lengths.

## State And Persistence
State touched is request read-result ownership and mount fd writes. Dependencies include `writev`, splice helpers, and `ReadResult`. Risks are splice short-read handling and ensuring `Done` is called.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State touched is request read-result ownership and mount fd writes. Dependencies include `writev`, splice helpers, and `ReadResult`. Risks are splice short-read handling and ensuring `Done` is called.

## Test Signals
State touched is request read-result ownership and mount fd writes. Dependencies include `writev`, splice helpers, and `ReadResult`. Risks are splice short-read handling and ensuring `Done` is called.
