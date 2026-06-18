# sources/sync-backup/syncthing/lib/connections/dialqueue.go

## sources/sync-backup/syncthing/lib/connections/dialqueue.go

Purpose: Orders pending device dial attempts to prefer likely useful connections while randomizing stale targets.

Important APIs/types/functions: `dialQueueEntry` stores device ID, last-seen time, short-lived flag, and targets. `dialQueue.Sort` sorts and shuffles entries.

Control flow and state: First sort puts non-short-lived, recently seen devices first and orders them by most recent `lastSeen`. Entries older than `recentlySeenCutoff` and short-lived entries are treated as stale; the stale suffix is shuffled to distribute attempts across old/unreliable devices.

Dependencies and integration: Uses `protocol.DeviceID`, `dialTarget` from connection structs, `recentlySeenCutoff` from service constants, and Syncthing `rand.Shuffle`.

Risks and test signals: Ordering affects connection fairness and startup convergence. `dialqueue_test.go` checks recent ordering and randomized stale/short-lived suffix behavior.
