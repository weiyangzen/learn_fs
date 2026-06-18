# sources/storage-engines/tikv/components/service/src/lib.rs

Purpose: crate root exposing the service event and service manager modules.

Important APIs: declares `pub mod service_event;` and `pub mod service_manager;`.

Control flow, state, and integration: no runtime logic here. It defines the public module surface used by `server2.rs`, signal handling, and status/control components.

Risks: minimal. Removing or privatizing either module breaks external imports.

Test signals: no direct tests.
