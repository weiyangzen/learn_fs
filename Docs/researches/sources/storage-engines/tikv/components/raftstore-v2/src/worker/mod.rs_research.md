# sources/storage-engines/tikv/components/raftstore-v2/src/worker/mod.rs

Purpose: this module file exposes raftstore-v2 worker submodules.

Important APIs/types/functions: public modules are `pd`, `refresh_config`, and `tablet`.

Control flow: no runtime logic here. Worker implementations are compiled through these module exports.

State and persistence: none directly.

Dependencies/integration: operation and batch code import PD/tablet worker tasks through this namespace.

Risks: minimal; removing an export breaks downstream module paths.

Test signals: downstream compilation.
