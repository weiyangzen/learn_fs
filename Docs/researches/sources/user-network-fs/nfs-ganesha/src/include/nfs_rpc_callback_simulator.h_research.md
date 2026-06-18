# sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback_simulator.h

## Purpose

`nfs_rpc_callback_simulator.h` declares lifecycle hooks for a callback simulator package intended to exercise or emulate NFSv4 callback dispatch behavior.

## Important APIs, Types, and Functions

The API is `nfs_rpc_cbsim_pkginit` and `nfs_rpc_cbsim_pkgshutdown`. The comments describe an intended small set of nonblocking backchannel service threads.

## Control Flow

Tests or optional simulator startup initialize the package before callback use and shut it down during cleanup. The implementation likely owns simulator threads and nonblocking socket state.

## State and Persistence Behavior

Any simulator state is process-local and should be removed on shutdown. It does not persist protocol state except through interactions with callback test clients.

## Dependencies and Integration Points

It depends on config and logging. It complements `nfs_rpc_callback.h` and is useful for callback/backchannel tests without requiring a full client implementation.

## Risks and Test Signals

Risks include simulator threads not stopping, mismatch with real callback semantics, and bitrot as v4.1 support evolves. Tests should init/shutdown repeatedly, run callback dispatch through simulator channels, verify nonblocking cleanup, and compare simulator behavior with real callback tests where possible.
