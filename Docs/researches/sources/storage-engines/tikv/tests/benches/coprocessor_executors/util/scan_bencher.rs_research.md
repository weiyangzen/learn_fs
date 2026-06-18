# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/scan_bencher.rs

## Purpose
This module provides generic scan benchmark abstractions shared by table scan and index scan benchmarks.

## Important APIs, Types, and Functions
`ScanExecutorBuilder` builds direct batch scan executors. `ScanExecutorDagHandlerBuilder` builds DAG handlers. `ScanBencher<P, M>` is the object-safe benchmark trait. `BatchScanNext1024Bencher<B>` adapts a scan executor builder to one-batch measurement. `ScanDagBencher<B>` adapts DAG handler builders and includes batch/normal tags plus display row count.

## Control Flow
Batch scan benching calls `B::build` and then `BatchNext1024Bencher`. DAG scan benching calls `B::build` with its batch flag and wraps the handler in `DagHandleBencher`. `box_clone` implementations allow input configurations to be duplicated for Criterion cases.

## State and Persistence Behavior
No persistent state is owned. Builder implementations in table/index modules decide store access.

## Dependencies and Integration Points
It depends on Criterion measurement traits, TiKV `RequestHandler`, batch executor interfaces, key ranges, column info, common benchers, and store descriptors.

## Risks and Test Signals
The abstractions assume builder-created executors are fresh and independent per iteration. Display names are used as Criterion parameters, so changes affect result continuity.
