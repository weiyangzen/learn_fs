# sources/object-store/rustfs/crates/protocols/src/sftp/mod.rs

## Purpose
`mod.rs` is the SFTP module facade. It documents architecture, declares submodules, applies platform-specific watchdog selection, and re-exports public entry points.

## Important APIs, Types, and Functions
Public exports are `SftpConfig`, `SftpInitError`, `SftpDriver`, `SftpError`, and `SftpServer`. Public submodules are `config` and `server`; private implementation modules include attrs, constants, dir, driver, errors, lifecycle, paths, read, read_cache, state, and write. `fallback_watchdog` is compiled on non-Linux targets, while `wedge_watchdog` is compiled on Linux.

## Control Flow
There is no runtime control flow in this file. The module declarations determine which implementation is available at compile time and the docs describe the high-level path from `SftpServer` through authentication, subsystem dispatch, and driver-backed S3 operations.

## State and Persistence Behavior
The facade owns no state. Its docs identify important stateful subsystems: per-session watchdog diagnostics, per-handle read caches, process-wide cache accounting, and environment-driven server configuration.

## Dependencies and Integration Points
It ties the SFTP feature into RustFS through re-exports and conditional modules. It documents Unix/Windows/unsupported-platform host-key behavior and SFTP-only channel behavior.

## Risks and Test Signals
Risks are architectural drift in exports, docs, or conditional modules. The compile-time test ensures `Protocol::Sftp`, `SftpConfig`, and `SftpInitError` remain available.
