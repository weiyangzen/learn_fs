# sources/object-store/rustfs/crates/obs/src/metrics/schema/mod.rs

## Purpose
Acts as the schema module index and re-export layer for RustFS metrics descriptors and primitives.

## Important APIs, Types, and Functions
Declares schema modules for audit, bucket, replication, cluster, system, node, notification, request, scanner, and entry primitives. Re-exports `MetricDescriptor`, `MetricName`, `MetricType`, `MetricNamespace`, `MetricSubsystem`, `subsystems`, and descriptor factories.

## Control Flow
No runtime control flow. Compilation makes all modules available and re-exported items are used throughout collectors and crate-level APIs.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
This module is imported by collectors and other observability code as the public schema surface. It connects many descriptor files to shared entry primitives.

## Risks
Adding a schema file without adding it here can leave descriptors inaccessible to collectors. Broad re-exports make it easy for downstream modules to depend on internal naming contracts. Duplicate concepts exist between node/process resource schemas and system process schemas, so module naming must remain clear.

## Test Signals
No direct tests. Build coverage is the primary signal: missing module declarations or broken re-exports fail compilation.
