# sources/object-store/rustfs/crates/audit/src/lib.rs

## Purpose

`lib.rs` defines the public module surface for the RustFS audit crate and re-exports the primary types used by other RustFS components.

## Important APIs and Types

It declares modules `entity`, `error`, `factory`, `global`, `observability`, `pipeline`, `registry`, and `system`. Public re-exports include `ApiDetails`, `AuditEntry`, `ObjectVersion`, `AuditError`, `AuditResult`, all global facade functions, `AuditMetrics`, `AuditMetricsReport`, `PerformanceValidation`, `AuditPipeline`, `AuditRuntimeFacade`, `AuditRuntimeView`, `AuditRegistry`, `AuditSystem`, and `AuditTargetMetricSnapshot`.

## Control Flow

There is no runtime control flow. The file controls how downstream crates import audit functionality and which modules are part of the stable crate API.

## State and Persistence

No state or persistence exists here. It exposes stateful modules such as `global`, `system`, `pipeline`, and `observability`.

## Dependencies and Integration Points

This is the integration gateway for RustFS request handlers, configuration loaders, metrics collectors, and tests. It hides some module path depth by re-exporting common types.

## Risks and Edge Cases

Wildcard re-export of `global::*` exposes all global helper functions and `AuditLogger`, so additions to `global.rs` automatically become public API. Re-exporting broad runtime types couples downstream crates to `registry` and `system` internals. Adding/removing re-exports can be a semver-significant API change.

## Test Signals

Compile tests or downstream crate builds should verify that intended imports continue to work. API review should accompany module or re-export changes.
