# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/mod.rs

## Purpose
Provides the public entry point for metric schema primitives and shared descriptor factory helpers.

## Important APIs, Types, and Functions
Declares submodules `descriptor`, `metric_name`, `metric_type`, `namespace`, `path_utils`, and `subsystem`. Exports factory functions `new_counter_md`, `new_gauge_md`, and `new_histogram_md`. Each factory accepts a metric name, help text, label slice, and subsystem, then creates a `MetricDescriptor` in the `RustFS` namespace.

## Control Flow
Factories convert labels from `&[&str]` to `Vec<String>`, coerce names and subsystems via `Into`, and call `MetricDescriptor::new()` with the appropriate `MetricType`.

## State and Persistence
No state is owned here. Factories return descriptor values that are usually stored in `LazyLock` statics by schema modules.

## Dependencies and Integration Points
This file is the primary dependency of all schema modules. It hides namespace choice and reduces descriptor boilerplate. `schema/mod.rs` re-exports these factories and primitive types.

## Risks
All factory-created descriptors are forced into the `RustFS` namespace; any future multi-namespace metrics need new APIs. The histogram helper is currently `allow(dead_code)` and may not be exercised by runtime collectors.

## Test Signals
The test validates histogram factory output, labels, namespace, subsystem formatting, full metric name generation, and custom subsystem path formatting.
