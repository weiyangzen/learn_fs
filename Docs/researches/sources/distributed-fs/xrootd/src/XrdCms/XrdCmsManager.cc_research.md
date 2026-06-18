# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsManager.cc

Purpose: implements the global manager-connection controller for cmsd: starting outbound manager connections, registering active manager nodes, broadcasting protocol messages to managers, handling redirects/reconfiguration, and verifying consistent cluster identity.

Important APIs/types/functions: `XrdCmsManager::{Add,Delete,Finished,Inform,Remove,Rerun,Reset,Run,Start,Verify}` and local scheduler job `XrdCmsDelNode`. Static shared state is `MTMutex`, `MastTab`, `MastSID`, and `MTHi`.

Control flow: `Start()` groups configured managers by site id, creates one `XrdCmsManager` per site, and calls `Run()`. `Run()` skips circular self-connections, allocates `XrdCmsProtocol` jobs for each target, resets `XrdCmsManList` and `XrdCmsManTree`, clears saved site identity, and schedules connection jobs. `Add()` registers a connected manager node in the static table unless reconfiguration is pending or `MTMax` is full. `Inform()` iterates active manager nodes, temporarily drops `MTMutex` while sending under node locks, and supports raw buffers, iovecs, or header+payload helpers. `Rerun()` parses a new manager list from a blacklist redirect, aborts the tree, marks current site nodes doomed/blacklisted, and sends disconnects. `Finished()` waits until all current manager connections drain, swaps in the pending list, clears old table entries, and restarts. `Verify()` stores the first seen site SID/name and rejects later managers for the same site with different cluster identity.

State and persistence behavior: in-memory topology state only. Static tables are shared across manager instances and persist for daemon lifetime. Per-instance state tracks current/pending manager lists, site id, current count, redirect flag, and first verified SID/site/host.

Dependencies: scheduler, CMS config/protocol/node/man-list/man-tree/routing/utils, `XrdOucTList`, `XrdNetAddr`, tokenizer, timers, and logging.

Integration points: `XrdCmsNode` uses `Inform()`, `Reset()`, and manager pointers. Protocol connection setup calls `Add()`, `Remove()`, `Finished()`, and `Verify()`. File/state/load notifications propagate upward through this class.

Risks: manager objects are intentionally never deleted. Static table operations require strict `MTMutex` discipline. `MastSID` is a `char` but site IDs are handled as ints up to `MTMax`; keeping values within range is essential. `Rerun()` mutates global connection state and marks nodes doomed while active sends may still be in progress. `Finished()` calls `Run()` while holding `MTMutex`, so nested lock behavior must remain safe.

Test signals: startup with multiple sites, self-connection filtering, max manager limit, broadcast under node removal, pending reconfiguration drain/restart, blacklist redirect flow, SID mismatch rejection, and race tests for add/remove/inform.
