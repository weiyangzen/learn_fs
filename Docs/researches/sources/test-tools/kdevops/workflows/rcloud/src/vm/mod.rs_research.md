<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/mod.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/vm/mod.rs

## Purpose
This module is the VM subsystem root for rcloud.

## Important APIs
It declares `disk`, `manager`, and `xml` submodules and re-exports `VmManager` and `VmSpec` from `manager`.

## Control Flow and Integration
There is no runtime control flow. API handlers import `crate::vm::{VmManager, VmSpec}` through this re-export, while the manager imports sibling `disk` and `xml` modules.

## State, Persistence, and Dependencies
No state is stored here. It defines module boundaries for disk persistence, libvirt lifecycle, and XML rendering.

## Risks and Test Signals
The re-export makes handler code independent of the manager file path but exposes the manager API as the VM module's public contract. Compile-time tests catch missing modules and changed exported names.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/vm/mod.rs -->
