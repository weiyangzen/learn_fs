# sources/object-store/minio/cmd/iam.go

## Purpose

`iam.go` is the top-level IAM subsystem coordinator. It initializes identity providers and policy plugins, chooses the IAM persistence backend, runs periodic refresh and watch handling, exposes user/group/policy/service-account APIs to the rest of the server, normalizes LDAP imports, purges stale external identities, and evaluates authorization decisions for regular users, STS credentials, and service accounts.

## Important APIs, Types, And Control Flow

`IAMSys` stores refresh metrics, provider configs, user-system type, role ARN policy mappings, the `IAMStoreSys`, refresh interval, and the `configLoaded` readiness channel. `Init` loads TLS STS, OpenID, LDAP, AuthN plugin, AuthZ plugin, and legacy OPA config with retry; initializes either `IAMObjectStore` or `IAMEtcdStore`; populates role mappings from OpenID/AuthN; writes the IAM format file if needed; loads IAM data; then starts `periodicRoutines`. `Load` delegates to `store.LoadIAMCache`, updates atomic refresh metrics, initializes site-replication service-account secret when present, and closes `configLoaded` on first success.

`periodicRoutines` starts backend watch handling when available and otherwise relies on randomized refresh intervals around the base interval. Each refresh reloads IAM data and hourly runs LDAP/OIDC purge/update routines. `loadWatchedEvent` maps changed storage keys to user, STS, service-account, group, policy, or policy-mapping notification handlers.

The public methods wrap store operations with initialization/readiness checks and peer notification when no backend watcher is present. They cover policy CRUD/info/listing, user create/delete/status/secret, group membership/status/listing, policydb attach/detach/set/query for built-in and LDAP identities, STS user creation/revocation, service-account create/update/list/get/delete, access-key listing, and account lookup. LDAP helpers normalize service-account parent/group DNs and imported policy-mapping keys while deleting extraneous non-normalized mappings.

Authorization uses `IsAllowed`. OPA/AuthZ plugin decisions take precedence. Owner credentials bypass policy checks. STS and service-account credentials are validated against parent claims, role ARN mappings, parent/user/group policy mappings, OpenID policy claims, and optional embedded session policies. Regular users resolve policy names through `PolicyDBGet` and evaluate the merged policy.

## State, Dependencies, Integration, Risks, And Tests

State includes global provider configs, role maps, refresh counters, persistent IAM store data, `configLoaded`, and cache data owned by `IAMStoreSys`. Dependencies include LDAP/OpenID/TLS identity config, AuthN/AuthZ plugins, OPA compatibility, madmin, auth credentials, policy evaluation, notification system, site replication hooks, and object/etcd stores. Risks include long initialization retries delaying IAM readiness, race-sensitive readiness behavior before `configLoaded`, watcher path parsing for slash-containing identities, peer notification duplication when watcher support changes, LDAP DN normalization conflicts, service-account session-policy size/claim correctness, root-access and owner bypass handling, and policy fallback from claims when mappings are absent. Test signals in this subset are indirect; the file is a coordinator whose behavior is typically covered by admin, STS, LDAP/OIDC, and authorization integration tests.
