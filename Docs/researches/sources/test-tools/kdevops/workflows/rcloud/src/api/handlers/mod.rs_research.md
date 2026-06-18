<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/mod.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/mod.rs

## Purpose
This module is the handler namespace aggregator for rcloud's API layer.

## Important APIs
It publicly declares `health`, `images`, `metrics`, and `vms` submodules. This makes the handlers available to route configuration and tests through `crate::api::handlers::*`.

## Control Flow and Integration
There is no runtime control flow. The integration point is `src/api/routes.rs`, which imports `super::handlers::{health, images, metrics, vms}` and binds functions from each module to URL paths.

## State, Persistence, and Dependencies
No state is stored here. Its dependency surface is only the module tree.

## Risks and Test Signals
The risk is namespace drift: adding a handler file without exporting it here makes it unavailable to route configuration. Compile-time tests catch missing modules. The existing health test indirectly validates this export path.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/api/handlers/mod.rs -->
