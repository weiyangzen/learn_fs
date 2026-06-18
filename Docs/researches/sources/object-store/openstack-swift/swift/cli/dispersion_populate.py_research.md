# sources/object-store/openstack-swift/swift/cli/dispersion_populate.py

Purpose: creates sample containers and objects spread across ring partitions so `swift-dispersion-report` can later measure missing replica coverage.

Important APIs: `put_container()`, `put_object()`, `report()`, and `main()`. Global counters track created items, retries, ETA, and current item type.

Control flow: `main()` monkey-patches eventlet, reads `dispersion.conf`, authenticates, chooses a storage policy, builds a `SimpleClient` pool, and separately populates containers and/or objects. For each target partition, it increments suffixes until ring placement hits an uncovered partition. `--no-overlap` first lists existing dispersion resources and removes already-covered partitions. GreenPool tasks create containers or objects and update progress.

State and persistence: writes real Swift containers named `dispersion_<policy>_<suffix>` and a container `dispersion_objects_<policy>` with objects named `dispersion_<suffix>`. Object data is the object name and metadata includes `x-object-meta-dispersion`.

Dependencies and integration: uses `swiftclient` or internal auth fallback, `SimpleClient`, Swift rings, storage policies, config parser, and eventlet pools.

Risks: it creates user-visible account resources and can collide with existing dispersion resources if prefixes are reused. Coverage math is partition-based, not replica-health-based. Authentication config and policy selection errors terminate with `exit()`.

Test signals: mock ring placement and client calls for coverage, no-overlap behavior, suffix-start options, policy lookup, retries accounting, and disabled object/container modes.
