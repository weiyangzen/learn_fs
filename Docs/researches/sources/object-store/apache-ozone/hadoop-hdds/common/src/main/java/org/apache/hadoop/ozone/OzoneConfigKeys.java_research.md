# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneConfigKeys.java

## Purpose
`OzoneConfigKeys` is the central public/unstable constant catalog for Ozone and HDDS configuration keys and defaults. It gives all components a shared spelling and default value source for ports, storage paths, security, ACLs, replication, Ratis, datastream, client behavior, HTTP/HTTPS, snapshots, SCM client settings, metrics, and other service features.

## Important APIs, types, and functions
- The class is `final`, has only `public static final` constants, and prevents construction with a private constructor.
- Key groups include container IPC/Ratis/datastream ports and random-port flags, metadata/db directory keys and permissions, chunk write and unsafe byte operation toggles, container cache settings, SCM block size, EC gRPC retries/timeouts, admin/read-only/blacklist users and groups, REST client connection limits, client socket/connection/read timeouts, replication defaults, list cache sizes, block and snapshot service intervals/timeouts/workers, Ratis settings delegated from `ScmConfigKeys`, datanode storage thresholds and RocksDB cache, security and HTTP security toggles, ACL authorizer settings, S3 volume and bucket layout defaults, client failover/follower-read settings, Freon HTTP settings, topology-aware read, OM lock sizing, HTTPS keystore/truststore keys, key provider cache, required OM version, listing page sizes, snapshot compaction knobs, SCM close wait, SCM client retry settings, and crypto compliance mode.
- Several constants reuse typed defaults from `ScmConfigKeys`, `ReplicationFactor`, `ReplicationType`, `HttpConfig.Policy`, `TimeDuration`, and `TimeUnit`.

## Control flow
There is no runtime control flow beyond class loading and static initialization of constants. Defaults that call methods such as `ReplicationFactor.THREE.toString()`, `HttpConfig.Policy.HTTP_ONLY.name()`, or `TimeUnit.*.toMillis(...)` are evaluated at class initialization.

## State and persistence behavior
The class stores immutable constant values. It does not read or persist configuration; other components use these keys with configuration sources to produce runtime behavior and persistent metadata locations.

## Dependencies and integration points
Dependencies include HDDS annotations, replication enums, `ScmConfigKeys`, Hadoop HTTP policy, and Ratis `TimeDuration`. Integration is broad: Ozone Manager, SCM, DataNode containers, S3 gateway, clients, Freon, security, snapshots, and metrics all reference this constant surface.

## Risks and edge cases
- Because constants are public and unstable, renames or default changes can silently alter cluster behavior or break configuration compatibility.
- Delegating some Ratis constants to `ScmConfigKeys` avoids duplication but couples this catalog to SCM defaults.
- Time defaults mix strings such as `30s`, milliseconds as `long`, and `TimeDuration`; callers must use the matching config parsing API.
- Security-related defaults are sensitive: `OZONE_SECURITY_ENABLED_DEFAULT` and HTTP security default false, while `OZONE_AUTHORIZATION_ENABLED_DEFAULT` true only takes effect when security or test authorization is enabled.
- Typographical compatibility matters; misspelled or legacy keys should not be "fixed" casually if users may already depend on them.

## Test signals
Tests should cover that key strings and defaults match generated docs/config references, secure/insecure defaults are interpreted correctly by `OzoneSecurityUtil`, Ratis constants mirror `ScmConfigKeys`, typed time and size defaults parse in component config loaders, and compatibility checks detect accidental key/default changes.
