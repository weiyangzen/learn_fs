# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/PipelineStateManagerImpl.java

## Purpose
`PipelineStateManagerImpl` is the concrete in-memory and DB-buffered implementation of `PipelineStateManager`, wrapped by an SCM Ratis proxy for replicated pipeline mutations.

## Important APIs, Types, And Functions
The builder accepts a pipeline DB table, node manager, SCM Ratis server, and DB transaction buffer, initializes the state map from the table, and returns a proxy handler. `initialize` loads persisted pipelines and repopulates node-to-pipeline membership. `addPipeline`, `removePipeline`, and `updatePipelineState` update `PipelineStateMap`, update `NodeManager` reverse indexes where needed, and buffer DB writes/removes. Read APIs delegate to `PipelineStateMap` under a read lock. Container membership methods add, force-add, remove, and list containers. `close` nulls the store, and `reinitialize` rebuilds state from a new table.

## Control Flow
`addPipeline` converts the protobuf pipeline to a `Pipeline`, then under write lock adds it to the state map, records node memberships, and adds it to the transaction buffer. `removePipeline` removes from the state map, removes node memberships, and buffers DB deletion; missing pipelines are logged as warnings because duplicate close/delete paths can occur. `updatePipelineState` converts protobuf state, updates the state map, then buffers the updated pipeline object. `removeContainerFromPipeline` deliberately swallows missing-pipeline exceptions because close-container and pipeline-close events can race through Ratis replay.

## State And Persistence Behavior
The class owns `PipelineStateMap`, `NodeManager`, a nullable `Table<PipelineID, Pipeline>`, `DBTransactionBuffer`, and a read/write lock. Persistence is transactional-buffer based rather than immediate direct table writes. When `pipelineStore` is null after close, mutations are skipped to avoid writes against a closed store. Reinitialize replaces both map and store and reloads from DB.

## Dependencies And Integration Points
It depends on `PipelineStateMap`, `NodeManager`, SCM HA Ratis proxy/invoker, DB table/iterator abstractions, transaction buffer, and pipeline/container types. It is constructed by `PipelineManagerImpl.newPipelineManager`.

## Risks And Edge Cases
Initialization must rebuild node reverse indexes exactly once; duplicate initialization without clearing node manager could over-retain memberships. Null `pipelineStore` silently prevents mutations after close, which protects shutdown but can hide late event activity. Missing-pipeline warnings are tolerated for idempotence, but excessive swallowing could mask real consistency bugs. `updatePipelineState` calls `getPipeline` while holding the write lock; this relies on the same `ReentrantReadWriteLock` allowing a writer thread to acquire the read lock.

## Test Signals
Tests should cover load from non-empty store, add/remove/update DB buffer operations, node manager add/remove pipeline calls, missing-pipeline idempotence, container membership add/remove/force rules, close behavior with null store, reinitialize replacing state, and Ratis proxy wrapping through the builder.
