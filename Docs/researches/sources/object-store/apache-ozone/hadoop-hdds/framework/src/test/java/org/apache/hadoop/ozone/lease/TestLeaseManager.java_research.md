# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/lease/TestLeaseManager.java

Purpose: Unit tests for `LeaseManager` acquisition, release, expiration, callbacks, reuse, and renewal.

Important APIs/types/functions: `LeaseManager`, `Lease`, `LeaseException`, `LeaseAlreadyExistException`, `LeaseNotFoundException`, `acquire`, `get`, `release`, `shutdown`, `start`, `hasExpired`, `getRemainingTime`, `getLeaseLifeTime`, and `renew`.

Control flow: Tests create a `LeaseManager<DummyResource>`, start it, acquire leases with default/custom timeouts and callbacks, assert duplicate acquisition and missing lease exceptions, release leases, sleep past expiration, verify callback execution or non-execution on release, reacquire resources after release/timeout, and renew a lease.

State and persistence behavior: All state is in-memory lease registry plus manager background expiration behavior. Callback tests mutate a map tracking lease status.

Dependencies and integration points: Uses a nested resource object with stable `equals`, `hashCode`, and `toString` to satisfy lease-map and error-message behavior.

Risks: Several tests sleep for lease duration plus one second, making the suite slow and timing-sensitive. Interrupted sleep retries full duration. Managers must be shut down to avoid lingering scheduler threads.

Test signals: Strong lifecycle signal for lease uniqueness, expiry removal, callback semantics, resource reuse, custom timeouts, and renewal.
