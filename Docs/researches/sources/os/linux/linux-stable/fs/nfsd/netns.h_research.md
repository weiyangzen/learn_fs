# File Research: sources/os/linux/linux-stable/fs/nfsd/netns.h

## Summary
Defines per-network-namespace NFSD state in `struct nfsd_net`.

## Contents
Tracks export/idmap caches, NFSv4 client/session/reclaim state, grace and lease state, duplicate reply cache state, per-net stats, service pointers, copy state, version enablement, server-to-server copy mounts, filecache disposal, localio clients, filehandle keying, and callback state.

## Important Details
The struct contains multiple synchronization domains: client mutex-protected lists/trees, `deleg_lock`, `client_lock`, `blocked_locks_lock`, seqlock-protected write verifier, per-net refcount/completions, and copy/localio spinlocks. Stats counters include duplicate reply cache metrics, stale filehandles, read/write byte counters, and NFSv4 operation counts.

## Risks
This is a central shared state object with many subsystem-owned fields. Callers need to respect each field’s documented lock or lifetime rule. Some duplicate reply cache stats are explicitly noted as not fully synchronized.
