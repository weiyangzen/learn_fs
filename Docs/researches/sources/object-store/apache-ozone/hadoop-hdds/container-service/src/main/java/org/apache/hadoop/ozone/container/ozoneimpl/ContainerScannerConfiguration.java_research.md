## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScannerConfiguration.java

Purpose: Defines configuration keys, defaults, validation, and accessors for datanode container scrub/scanner behavior.

Important APIs and functions: Config fields include global scanner enablement, developer data/metadata scanner toggles, metadata scan interval, data scan interval, background and on-demand bandwidth per volume, and minimum per-container scan gap. `validate()` resets negative values to defaults and logs warnings. Setters/getters expose selected fields for tests and runtime config injection.

Control flow and state: Annotated with `@ConfigGroup(prefix = "hdds.container.scrub")`; fields are populated by the HDDS config system and validated after construction. Defaults are 3h metadata interval, 7d data interval, 5 MB/s bandwidth, and 15m min gap.

Persistence and dependencies: Configuration is not persisted here. It controls scanner scheduling, throttling, and scan skipping in `BackgroundContainer*Scanner`, `OnDemandContainerScanner`, and `ContainerScanHelper`.

Risks: Constant names for developer toggles include both `DEV_DATA_ENABLED` strings and config keys with `.dev.data.scan.enabled`; callers should use the annotated keys. Negative min-gap warning logs the key constant as default in one message but sets the numeric default. Runtime changes after scanner construction may not affect already-created helpers/throttlers.

Test signals: Config binding, default values, negative validation for all numeric fields, enabled/toggle getters, scan interval setters, min-gap setter, and scanner construction consuming intervals/bandwidth.
