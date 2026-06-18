# sources/storage-engines/foundationdb/fdbrpc/Locality.cpp

`Locality.cpp` implements locality constants, process-class parsing/formatting, role fitness scoring, and load-balance distance classification.

Static `LocalityData` keys define process, zone, data-center, machine, and data-hall identifiers. `ProcessClass` constructors parse class/source strings; `toString()` and `sourceString()` serialize them; `machineClassFitness(ClusterRole)` ranks the current class for each cluster role; and `loadBalanceDistance()` classifies endpoints as same machine, same data center, or distant based on locality IDs and knobs.

Control flow is mostly switch/cascade policy. Class parsing maps known strings to enum values, maps deprecated `proxy` to `commit_proxy` with a warning, and asserts for deprecated `fast_restore`. The fitness matrix encodes role recruitment preferences across storage, logs, proxies, resolvers, cluster controller, data distributor, ratekeeper, consistency scan, blob roles, backup, and encryption key proxy. Distance checks zone ID first, then data-center ID, then distant.

State is static constants and in-memory `ProcessClass` values. Dependencies are `fdbrpc/Locality.h` and Flow knobs. Integration is broad: recruitment, configuration parsing, locality-aware placement, and load-balanced request distance all depend on these rules.

Risks include regressions when adding roles/classes, invalid-string handling, deprecated class assertions, and knob-gated distance behavior. There are no direct tests here; coverage is indirect through simulation placement, configuration, and load-balancing behavior.
