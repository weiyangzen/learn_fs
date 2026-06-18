# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerPrepareState.java

## Purpose
`OzoneManagerPrepareState` owns the in-memory and marker-file portion of OM prepare mode. Prepare mode blocks ordinary write requests while allowing only `Prepare` and `CancelPrepare`, and records a marker file so an OM remains prepared after restart.

## Important APIs, types, and functions
- `NO_PREPARE_INDEX` is the sentinel for no prepared index.
- Constructors either initialize `NOT_PREPARED` state or restore from an existing marker file against the current transaction index.
- `enablePrepareGate()` moves to `PREPARE_GATE_ENABLED` and clears the index.
- `cancelPrepare()` clears the gate/index/status and deletes the marker file.
- `finishPrepare(long)` enables the gate, writes the marker file, and marks `PREPARE_COMPLETED`.
- `restorePrepareFromIndex(...)` and `restorePrepareFromFile(...)` validate restored prepare index against current index and rebuild prepared state.
- `requestAllowed(Type)` enforces the write gate.
- `getState()` returns a snapshot object containing index and protobuf `PrepareStatus`.
- `getPrepareMarkerFile()` maps configuration to `<ozone metadata dir>/current/<PREPARE_MARKER>`.

## Control flow
The normal prepare flow first calls `enablePrepareGate()` to reject future writes, then `finishPrepare(index)` to write the marker and set completed status once the prepare point is known. Startup/snapshot recovery flows read either a DB marker from `OzoneManager` or the local marker file, then call `restorePrepareFromIndex` or `restorePrepareFromFile`. All public mutating/read methods are synchronized to keep gate, index, and status consistent.

## State and persistence behavior
State is three synchronized fields: `prepareGateEnabled`, `prepareIndex`, and `status`. Persistence is a UTF-8 marker file containing the prepare log index. Marker file read, parse, write, and delete errors become `OMException` with `PREPARE_FAILED`. The class does not write the DB prepare marker; `OzoneManager` reconciles that Ratis-replicated state with this local file.

## Dependencies and integration points
It integrates with `OzoneManagerStateMachine.preAppendTransaction` and `OzoneManagerRatisServer.submitRequest`, which use `requestAllowed` to block writes. `OzoneManager.instantiatePrepareStateOnStartup()` and `instantiatePrepareStateAfterSnapshot()` coordinate this class with transaction info and DB markers. It uses `ServerUtils.getOzoneMetaDirPath`, `OMStorage.STORAGE_DIR_CURRENT`, and `OzoneConsts.PREPARE_MARKER` for file location.

## Risks and edge cases
The class reads the marker file with one `stream.read(data)` call, which assumes the requested byte count is returned. A malformed marker, unreadable marker, missing marker during explicit restore, or marker index greater than current index all fail prepare recovery. `restorePrepareFromIndex` writes the restored index to disk but stores `currentIndex` in memory, so callers must understand the difference between requested prepare point and current applied index.

## Test signals
Tests should cover fresh state, gate request filtering, prepare/cancel idempotence, marker file creation/deletion path, malformed marker content, missing marker restore, marker index greater than current index, restoration with and without writing the marker, and concurrent reads of `getState()` while state transitions occur.
