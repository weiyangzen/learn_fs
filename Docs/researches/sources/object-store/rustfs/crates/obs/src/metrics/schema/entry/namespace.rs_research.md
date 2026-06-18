# sources/object-store/rustfs/crates/obs/src/metrics/schema/entry/namespace.rs

## Purpose
Defines the top-level metric namespace enum.

## Important APIs, Types, and Functions
`MetricNamespace` currently has one variant, `RustFS`. `as_str()` maps it to `rustfs`.

## Control Flow
`as_str()` is a simple match and is called during full metric name construction.

## State and Persistence
No runtime state or persistence.

## Dependencies and Integration Points
Used by `MetricDescriptor` and all factory-created descriptors. It fixes the first segment of exported metric names.

## Risks
The one-namespace design is simple but inflexible. Adding another namespace later requires updating factories or adding new factory variants; otherwise everything remains `rustfs_*`.

## Test Signals
No local tests. Descriptor tests indirectly verify `RustFS` maps to `rustfs`.
