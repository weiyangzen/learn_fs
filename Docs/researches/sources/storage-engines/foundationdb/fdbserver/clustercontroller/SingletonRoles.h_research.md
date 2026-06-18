# sources/storage-engines/foundationdb/fdbserver/clustercontroller/SingletonRoles.h

## Purpose
`SingletonRoles.h` defines lightweight wrappers for cluster-controller-managed singleton roles: ratekeeper, data distributor, and consistency scan. The wrappers provide a common shape for checking presence, publishing role interfaces into `ServerDBInfo`, halting existing singletons, and triggering recruitment. The file also defines a recruitment throttler for singleton re-recruit attempts.

## Important APIs, Types, and Functions
- `PID_USED_AMP_FOR_NON_SINGLETON` is a placement weighting constant used elsewhere to make processes already occupied by non-singleton roles less attractive for singleton placement.
- `template <class Interface> class Singleton` stores a reference to an `Optional<Interface>` and exposes `getInterface()` and `isPresent()`.
- `RatekeeperSingleton` maps to `Role::RATEKEEPER` and `ProcessClass::Ratekeeper`, writes `cc.db.setRatekeeper()`, sends `HaltRatekeeperRequest`, and triggers `cc.recruitRatekeeper`.
- `DataDistributorSingleton` maps to `Role::DATA_DISTRIBUTOR` and `ProcessClass::DataDistributor`, writes `cc.db.setDistributor()`, sends `HaltDataDistributorRequest`, and triggers `cc.recruitDistributor`.
- `ConsistencyScanSingleton` maps to `Role::CONSISTENCYSCAN` and `ProcessClass::ConsistencyScan`, writes `cc.db.setConsistencyScan()`, sends `HaltConsistencyScanRequest`, and triggers `cc.recruitConsistencyScan`.
- `SingletonRecruitThrottler::newRecruitment()` returns the wait time needed to enforce `SERVER_KNOBS->CC_THROTTLE_SINGLETON_RERECRUIT_INTERVAL` between recruitment starts and records the current start time.

## Control Flow
Cluster-controller code can instantiate the appropriate singleton wrapper around an optional interface. If present, `setInterfaceToDbInfo()` publishes it to the database info and emits a trace event. `halt()` sends the relevant halt RPC to the worker/process recorded by process ID and stores a future in `cc.id_worker[pid]` so broken promises become non-failing `Never()` futures. `recruit()` updates `cc.lastRecruitTime` and sets the role-specific recruitment trigger.

The throttler is call-based: each recruitment start calls `newRecruitment()`, receives a non-negative delay, and updates `lastRecruitStart` to the current time. The first call starts from `-1`, so the computed wait is normally zero after process uptime exceeds the configured interval.

## State and Persistence Behavior
This header has no durable persistence. The singleton wrappers mutate in-memory cluster-controller state: `ServerDBInfo` via `cc.db`, worker halt futures via `cc.id_worker`, recruitment triggers, and `lastRecruitTime`. The singleton interface reference is borrowed from a caller-owned `Optional<Interface>`, so lifetime is external. `SingletonRecruitThrottler` stores only `lastRecruitStart`.

## Dependencies and Integration Points
The header depends on `ClusterController.h`, `RatekeeperInterface.h`, and `DataDistributorInterface.h`. `ConsistencyScanInterface` is available through the included cluster-controller-related headers. Integration points include cluster-controller role tracking, process-class fitness/recruitment code, singleton halt endpoints, and `ServerDBInfo` publication consumed by clients and other server roles.

## Risks and Edge Cases
- `Singleton::getInterface()` calls `Optional::get()` without checking presence; callers must use it only after `isPresent()` or equivalent logic.
- `RatekeeperSingleton` and `DataDistributorSingleton` check both interface presence and `cc.id_worker.contains(pid)` before assigning halt futures. `ConsistencyScanSingleton::halt()` checks only interface presence before indexing `cc.id_worker[pid]`, which can create or access an entry for an absent process ID depending on map semantics; this asymmetry is worth reviewing.
- The wrappers store references to optional interfaces. They should not outlive the optional values they wrap.
- Recruitment trigger methods do not themselves throttle; callers must use `SingletonRecruitThrottler` or equivalent scheduling.
- `PID_USED_AMP_FOR_NON_SINGLETON` assumes fewer than 100 singleton roles; adding many singleton role types would require revisiting placement weighting.

## Test Signals
Useful tests would cover publishing each singleton into `ServerDBInfo`, halting only the intended worker endpoint, recruitment trigger setting, throttler wait-time calculations, and absent-interface no-op behavior. Existing trace event names `CCRK_SetInf`, `CCDD_SetInf`, and `CCCK_SetInf` provide operational evidence that singleton interfaces were published.
