# sources/storage-engines/foundationdb/fdbctl/ExcludeCommand.cpp

## Purpose
This file implements gRPC exclusion management for `fdbctl`: excluding addresses/localities, checking in-progress exclusions, and reporting excluded/failed status.

## Important APIs, Types, And Functions
Utility readers include `utils::getExcludedServers`, `getFailedServers`, `getExcludedLocalities`, `getFailedLocalities`, and `getInProgressExclusion`. Mutating/control functions include `excludeServersAndLocalities`, `checkForExcludingServers`, `exclude`, and `excludeStatus`.

## Control Flow
Status helpers read management special-key ranges and strip range prefixes. `exclude` concurrently fetches worker process data and storage server interfaces, builds exclusion sets from requested localities and processes, validates non-empty input, writes exclusions/failed exclusions with optional force flags, then waits or checks in-progress exclusions according to `no_wait`. It populates response fields for excluded addresses, data movement completion, and absent addresses. `excludeStatus` aggregates excluded, failed, locality, and in-progress data into the reply.

## State And Persistence Behavior
Exclusion state is persisted in FoundationDB management special keys under excluded/failed address and locality ranges. Force options are written as special option keys in the same transaction. Local state consists of temporary sets/maps of worker and storage addresses.

## Dependencies And Integration Points
It depends on `ControlCommands.h`, FoundationDB management/special-key APIs, storage server interfaces, worker locality helpers such as `getAddressesByLocality`, Flow actors, Boost joining, and gRPC status types.

## Risks And Edge Cases
`ExcludeRequest.hosts` and `all` are defined in the proto but are not handled here; only `localities` and `processes` are considered. Invalid process addresses return `INVALID_ARGUMENT` with an empty message. The internal error format `fmt::format("error: ", e.name())` omits the error name because the format string lacks a placeholder. Waiting uses polling with jitter rather than watches. A stray `I` appears in the license comment.

## Test Signals
Tests should cover process exclusion, locality exclusion, failed exclusion, force flags, `no_wait`, absent-address reporting, in-progress migration reporting, include/exclude round trips, unsupported `hosts`/`all` fields, and special-key API failure propagation.
