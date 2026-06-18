# sources/storage-engines/foundationdb/fdbclient/LocalClientAPI.h

## Purpose
`LocalClientAPI.h` declares the local client API accessor used by in-process FoundationDB code.

## Important APIs, Types, And Functions
It includes `fdbclient/IClientApi.h` and declares `IClientApi* getLocalClientAPI();`.

## Control Flow
This header has no runtime control flow. The implementation in `LocalClientAPI.cpp` provides a singleton `ThreadSafeApi`.

## State And Persistence Behavior
The header owns no state. The declared function returns process-local client API state that can be used to access persistent FoundationDB data.

## Dependencies And Integration Points
It uses both an include guard and `#pragma once`, and depends on the `IClientApi` interface. It is consumed by local client API bootstrap/linkage code.

## Risks And Edge Cases
The raw pointer return type exposes no ownership in the type system; callers must treat it as borrowed singleton state.

## Test Signals
Successful compilation of users and link tests for `getLocalClientAPI()` validate the declaration. Runtime validation comes from operations through the returned API.
