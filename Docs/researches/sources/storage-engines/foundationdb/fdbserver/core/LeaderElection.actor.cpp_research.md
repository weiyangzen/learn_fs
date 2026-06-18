# sources/storage-engines/foundationdb/fdbserver/core/LeaderElection.actor.cpp

## Purpose
Implements client-side leader election against the coordinator leader-election register. It submits candidacy, observes coordinator nominees, handles coordinator forwarding, publishes the elected leader interface, and maintains leadership through heartbeats.

## Important APIs, Types, and Functions
- `submitCandidacy()` repeatedly sends `CandidacyRequest`s to one coordinator and updates a shared nominee slot.
- `buggifyDelayedAsyncVar()` wraps an `AsyncVar` with delayed propagation for simulation eventual-consistency testing.
- `changeLeaderCoordinators()` sends `ForwardRequest`s to old coordinators and waits for quorum.
- `tryBecomeLeaderInternal()` is the main actor for candidacy, election observation, forwarding, leadership acquisition, and heartbeat maintenance.

## Control Flow
The actor optionally delays startup for poor recruitment priority. It then repeatedly creates a new `LeaderInfo` change ID, submits candidacy to every coordinator, watches the aggregate nominees via `getLeader(nominees)`, and updates `outSerializedLeader` when another leader is known. If coordinators report forwarding, it writes forwarding to a quorum, persists the new connection string, and throws `coordinators_changed()`.

When this candidate is elected by a connected quorum, it publishes its serialized interface and enters heartbeat mode. Each heartbeat round sends `LeaderHeartbeatRequest` to coordinators and races majority-true, majority-false, timeout, and priority changes. Majority false or timeout causes the actor to release leadership and restart candidacy.

## State and Persistence Behavior
Most state is actor-local: nominee slots, `myInfo`, candidacy futures, previous change ID, and leadership flag. Persistent behavior occurs through `coordinators.ccr->setAndPersistConnectionString()` when forwarding is detected. Coordinator-side forwarding persistence is handled by `Coordination.cpp`.

## Dependencies and Integration Points
Depends on failure monitor/locality headers, coordination interfaces, monitor-leader types, server knobs, Flow actors, and `getLeader()` logic from the leader-election API. It integrates with cluster controllers and other leader candidates that need a serialized leader interface.

## Risks and Edge Cases
Forwarding can wait up to 20 seconds for old coordinator quorum before proceeding with the received connection string. Bad candidate timeout changes IDs when a candidate appears to block election progress. Heartbeat timeout gives up leadership under poor communication even without majority false. Buggified async variables intentionally delay observed leader publication in simulation.

## Test Signals
No embedded tests in this file. Coverage should come from simulation leader-election workloads, coordinator forwarding/quorum-change tests, priority-change tests, and network partition scenarios.
