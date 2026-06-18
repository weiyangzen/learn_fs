# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/mod.rs

Purpose: this module file groups unsafe recovery operation extensions for raftstore-v2 peers and store FSMs.

Important APIs/types/functions: it declares private submodules `create`, `demote`, `destroy`, `force_leader`, and `report`. The public API is provided by inherent impl blocks in those files on `Store` and `Peer`.

Control flow: importing this module compiles all unsafe recovery handlers into the broader `operation` module. Dispatch occurs through router messages and peer/store handlers elsewhere; this file itself contains no runtime logic.

State and persistence: no direct state. State is owned by submodules via `ForceLeaderState`, `UnsafeRecoveryState`, raft admin proposals, split-init creation, and destroy progress.

Dependencies/integration: serves as the integration point tying unsafe recovery operations into raftstore-v2 operation compilation.

Risks: because all submodules are private and expose inherent methods, missing this module import would silently remove unsafe recovery behavior from operation builds.

Test signals: no tests here; testing is by submodule behavior.
