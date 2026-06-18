# sources/storage-engines/foundationdb/fdbserver/coordinator/include/fdbserver/coordinator/CoordinationServer.h

## Purpose
Public coordinator-server header exporting the actor entry points implemented in `Coordination.cpp`.

## Important APIs, Types, and Functions
- `coordinationServer(std::string dataFolder, Reference<IClusterConnectionRecord> ccf)` starts the coordinator service for a process data folder.
- `coordChangeClusterKey(std::string dataFolder, KeyRef newClusterKey, KeyRef oldClusterKey)` rewrites coordinator persistence after a cluster key update.

## Control Flow
This file contains declarations only. Runtime control flow is in `Coordination.cpp`.

## State and Persistence Behavior
The header itself owns no state. The exported functions imply access to coordinator-local persistence through `dataFolder` and cluster-file state through `IClusterConnectionRecord`.

## Dependencies and Integration Points
Includes `fdbserver/core/CoordinationInterface.h` for the coordination-related types. Included by server code that starts coordinator actors or invokes cluster-key migration.

## Risks and Edge Cases
The include guard and `#pragma once` are redundant but harmless. API signatures expose strings and `KeyRef`s; callers must ensure referenced key memory remains valid for actor execution according to Flow conventions.

## Test Signals
Validated indirectly by link tests and by any simulation that starts coordinator roles or changes cluster keys.
