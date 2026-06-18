# sources/storage-engines/tikv/src/server/lock_manager/deadlock.rs

Purpose: implements distributed deadlock detection for pessimistic transactions by maintaining a TTL-bound wait-for graph on a single elected detector leader and forwarding follower wait events to that leader.

Important APIs/types/functions: `DetectTable` stores wait edges and exposes `detect`, cleanup, TTL reset, and wait-chain generation. `Scheduler` wraps `FutureScheduler<Task>`. `RoleChangeNotifier` observes raftstore region/role changes for the leader region containing `LEADER_KEY`. `Detector` owns leader/follower behavior. `Service` exposes deadlock gRPC.

Control flow: local lock waits schedule `Task::Detect`. Leaders process events in `handle_detect_locally`; followers discover the leader via PD, resolve its address, establish a streaming `Client`, and forward `DeadlockRequest`s. `DetectTable::detect` expires old edges, refreshes duplicate edges, searches from lock owner back toward waiter, returns a deadlock key hash plus wait chain if a cycle is found, otherwise registers the edge. Cleanup tasks remove a single lock digest or all entries for a transaction. Incoming remote streams are accepted only while the node is leader.

State and persistence: the wait-for graph, role, cached leader info, and leader client are in memory. Role changes reset graph/client state. Edges expire by timeout and active cleanup. There is no disk persistence; correctness relies on retries/timeouts if detect requests are dropped.

Dependencies and integration: integrates with PD for leader region lookup, store address resolver, raftstore coprocessor observers, gRPC `deadlock` service, waiter manager callbacks, `txn_types::TimeStamp`, and lock diagnostic context including resource group tags.

Risks: dropped follower detect requests can delay deadlock reporting until transaction timeout/retry. Active expiration scans only after a large threshold and interval, so low-volume stale edges are mainly cleaned during searches. Leader changes clear state and can miss transient cycles. The graph stores one diagnostic key per hash, so hash collisions may reduce diagnostic precision.

Test signals: tests cover cycle detection, edge cleanup, TTL expiration, wait-chain reconstruction across graph shapes, role-change notifier behavior for create/update/destroy events, and leader/follower role transitions.
