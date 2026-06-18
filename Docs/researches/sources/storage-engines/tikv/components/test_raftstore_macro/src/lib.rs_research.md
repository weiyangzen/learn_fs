# Research: sources/storage-engines/tikv/components/test_raftstore_macro/src/lib.rs

## sources/storage-engines/tikv/components/test_raftstore_macro/src/lib.rs

Purpose: implements the `#[test_case(path::to_cluster_ctor)]` proc macro that turns one generic test body into a module containing one concrete `#[test]` per annotated cluster constructor. It lets raftstore tests run the same body across node/server/v2 cluster builders.

The public API is `test_case(arg, input)`. It parses the input as `ItemFn`, collects the current macro argument and any remaining `#[test_case(...)]` attributes, removes the duplicate attributes from the cloned function, and delegates to `render_test_cases`. Rendering clones the function per case, parses package and method identifiers with `parse_test_case`, inserts `use package::{util::*, method as new_cluster, Simulator};`, adds `#[test]`, renames the function to `package_method`, and wraps all generated tests in a `#[cfg(test)] mod original_name`.

State is entirely compile-time token state; no runtime persistence. Dependencies are `syn`, `quote`, `proc_macro2`, and compiler `proc_macro`.

Risks are parser fragility: `parse_test_case` manually walks token trees and assumes simple `package::method` forms, not arbitrary paths, aliases, generics, or nested modules. It panics on invalid streams, which becomes a compile error. Name generation can collide if package/method combinations normalize identically. Test signals are compile-time expansion of multi-attribute examples and downstream tests that rely on `new_cluster` and `util::*` imports.
