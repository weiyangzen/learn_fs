# sources/distributed-fs/xrootd/src/XrdCl/XrdClForkHandler.hh

## Purpose
`XrdClForkHandler.hh` declares the object registry and lifecycle hooks used to make XrdCl safe around process forks.

## Important APIs, Types, And Functions
`ForkHandler` exposes registration methods for `FileStateHandler`, `FileSystem`, `PostMaster`, and `FileTimer`, plus `Prepare`, `Parent`, and `Child`. File and filesystem registration methods mutate protected `std::set` collections. `RegisterPostMaster` and `RegisterFileTimer` store singleton pointers.

## Control Flow
The class is meant to be registered with `pthread_atfork` or an equivalent environment-level hook. Before fork, it locks runtime objects and stops background work. After fork, it unlocks and either restarts the parent runtime or reconstructs child runtime state.

## State And Persistence Behavior
All state is process-local and pointer-based. The class does not own registered objects; it only tracks them for locking and callbacks.

## Dependencies And Integration Points
It forward-declares the main participants and depends on `XrdSysPthread` and `std::set`. `FileSystem` registers non-plugin instances, while file state handlers and default environment components register elsewhere.

## Risks And Test Signals
Because registration uses raw pointers, destruction without unregistering can lead to invalid callbacks during fork. Tests should cover concurrent registration while forking, missing postmaster/timer registration, and duplicate register/unregister behavior.
