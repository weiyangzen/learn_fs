# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ConfigurationProvider.java

## Purpose
`ConfigurationProvider` exposes the CLI-created `OzoneConfiguration` to Guice/Jersey/CDI-managed Recon components as a singleton provider and registers deprecated key aliases.

## Important APIs, Types, And Functions
It implements `Provider<OzoneConfiguration>`. Static methods `setConfiguration` and `resetConfiguration` are visible for tests. `addDeprecations` maps legacy Recon HTTP and Kerberos configuration keys to current `ReconServerConfigKeys`.

## Control Flow
The static initializer registers deprecations once. `ReconServer.call()` sets the configuration before Guice object creation. `get()` returns the static configuration reference.

## State And Persistence
State is a process-wide static `OzoneConfiguration`. No persistent data is written.

## Dependencies And Integration Points
It integrates Hadoop `Configuration.addDeprecations`, Guice provider binding in `ReconControllerModule`, and `ReconServer` startup. Tests and MiniOzoneCluster can pre-populate the static value.

## Risks
The static configuration is global and only set when currently null, so tests must call `resetConfiguration` for isolation. If startup forgets to set it, Guice consumers receive null.

## Test Signals
Tests should verify deprecation mappings, single-assignment behavior, reset behavior, and successful injection into modules.
