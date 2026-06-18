## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/OzoneConfiguration.java

Purpose: Ozone/HDDS-specific Hadoop `Configuration` subclass and `MutableConfigurationSource` implementation.

Important APIs: static `of` adapters, `newInstanceOf`, constructors, XML property unmarshalling classes, `getConfigurationResourceFiles`, `activate`, `getAllPropertiesByTag`, `getOzoneProperties`, config key iteration, prefix-trimming lookup, tag recognition, deprecated-key registration, fallback `getInt`, `reloadConfiguration`, guarded `getProps`, `getOrFixDuration`, and iterator.

Control flow: static initialization registers deprecations and activates default resources. Resource activation includes Hadoop defaults/sites, generated module defaults, `ozone-default.xml`, and `ozone-site.xml`. `getProps` lazily wraps Hadoop properties in `DelegatingProperties`, reading crypto compliance mode without compliance checks and crypto-tagged properties through Hadoop tag APIs. Reload resets the cached wrapper. `getAllPropertiesByTag` reloads props first and overlays current values because the superclass can miss overridden untagged values.

State/persistence: mutable Hadoop config plus cached delegating properties. Dependencies: Hadoop `Configuration`, JAXB, config tags, Ozone/SCM/HDDS keys, Ratis keys, and `DelegatingProperties`.

Integration points: nearly every service config read, generated config beans, deprecated Hadoop/Ozone keys, Ratis property propagation, crypto compliance policy, and XML config tooling. Risks: static default resource registration affects global Hadoop configuration; `of(ConfigurationSource)` casts non-legacy sources to `OzoneConfiguration`; cached `delegatingProps` must be invalidated on reload; fallback `getInt` logs even when fallback is null; Hadoop 2 tag API absence disables crypto compliance tag lookup. Test signals: default resource ordering, deprecated key mappings, compliance wrapper behavior, reload invalidation, prefix trimming, invalid duration auto-fix, XML unmarshalling, and adapter casts.
