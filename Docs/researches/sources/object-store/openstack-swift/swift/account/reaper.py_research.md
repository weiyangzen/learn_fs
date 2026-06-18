# sources/object-store/openstack-swift/swift/account/reaper.py

## Purpose
Defines the account reaper daemon, which deletes containers and objects belonging to accounts marked deleted. It scans local primary account DBs, deletes objects through object servers, deletes containers through container servers, and records progress metrics.

## Important APIs, Types, and Functions
`AccountReaper` extends `Daemon`. Initialization reads devices, mount checking, interval, Swift directory, timeouts, bind IP/port, concurrency, DB preallocation, delay/reap warning settings, and creates green pools. Ring helpers are `get_account_ring`, `get_container_ring`, and `get_object_ring`. Main work methods are `run_forever`, `run_once`, `reap_device`, `reset_stats`, `reap_account`, `reap_container`, and `reap_object`. `main()` parses daemon options and runs the daemon.

## Control Flow
`run_forever` sleeps a randomized initial offset and repeatedly calls `run_once`. `run_once` iterates devices, validates mounted drives, and calls `reap_device`. `reap_device` walks account DB paths by partition/suffix/hash, checks whether the local device is a primary for the partition, opens account DBs, and reaps those with deleted status and non-empty listings.

`reap_account` enforces delay_reaping, pages through containers, shards container ownership when multiple account primaries exist, spawns `reap_container`, waits, logs stats, and warns if an account remains unreaped too long. `reap_container` lists objects from a selected container node, spawns object deletes, then sends container deletes to all container nodes with account update headers. `reap_object` gets the policy-specific object ring and sends object deletes to all object nodes with container update headers.

## State and Persistence Behavior
The reaper reads account DBs from the account datadir and mutates cluster state via direct DELETE requests. It does not remove account DBs itself; final DB reclamation is left to account replication/reclaim. In-memory counters track return code classes and deleted/remaining/possibly remaining objects and containers for logging/metrics.

## Dependencies and Integration Points
Depends on eventlet-style `GreenPool`, `Timeout`, Swift rings, direct client functions, `AccountBroker`, `check_drive`, storage policies, request helper headers, daemon utilities, logging utilities, and account/container/object server direct APIs.

## Risks and Edge Cases
Concurrency is split as square root of configured concurrency, so non-square values create float pool sizes if the GreenPool implementation does not coerce. The chosen container listing node is `nodes[-1]`, so failures there can leave containers remaining until retry. Partial success increments "possibly remaining" stats. Policy lookup failures leave objects remaining. The code updates object stats inside the loop over object nodes, which may overcount per-object outcomes if this exact version is used. Reaper safety depends on correct primary-device detection and replication network headers.

## Test Signals
Good tests should mock rings and direct clients to cover deleted account discovery, delay_reaping, container shard selection, object delete success/failure/timeout, invalid policy, stats accounting, and warning thresholds. Operational signals are reaper logs, return-code metrics, and decreasing container/object counts for deleted accounts.
