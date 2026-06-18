# sources/object-store/openstack-swift/swift/common/exceptions.py

Purpose: defines Swift's shared exception taxonomy for disk files, rings, replication, memcache, clients, timeouts, listing iterators, encryption, and process management.

Important APIs/types/functions: `MessageTimeout` extends Swift `Timeout` with a message; `SwiftException` is the base for many domain exceptions; disk-file exceptions distinguish missing, deleted, expired, quarantined, collision, no space, unavailable device, xattr, and metadata checksum states; ring exceptions distinguish load/build/validation problems; replication lock and partition lock exceptions specialize `LockTimeout`; memcache exceptions communicate connection, incr race, and pool timeout failures; `ClientException` carries HTTP scheme/host/port/path/query/status/reason/device/body/headers and formats them into a useful string; `InvalidPidFileException` protects process management.

Control flow: most classes are markers. `DiskFileDeleted` derives a `Timestamp` from metadata or zero. `ListingIterNotAuthorized` stores the auth response. `ClientException.__str__` incrementally appends URL, status, reason, device, and short response content to the base message.

State and persistence: exception instances store transient context only. No persistent state is modified.

Dependencies and integration: imports Swift concurrency `Timeout` and timestamp handling. These exceptions are used throughout storage, proxy, ring, replication, memcache, and manager code to communicate typed failures without circular definitions.

Risks: marker classes rely on callers catching the correct subclass; some names intentionally shadow Python built-ins (`FileNotFoundError`, `PermissionError`) within this module; `ClientException` only includes the first 60 response chars; `PutterConnectError` does not call `Exception.__init__`. Tests should cover string formatting, deleted timestamp defaults, timeout string formatting, and catch hierarchies expected by diskfile, proxy, and replication code.
