## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/DelegatingProperties.java

Purpose: `Properties` wrapper used by `OzoneConfiguration` to enforce crypto compliance restrictions while delegating storage and mutation to an underlying `Properties`.

Important APIs: constructor with base properties, compliance mode, and crypto-tagged properties; `checkCompliance`; overridden `getProperty`, mutation and collection methods; `iterator()` returning checked string key/value entries.

Control flow: compliance checking is enabled unless mode is `unrestricted`. For crypto-tagged configs except the compliance mode key itself, the value must appear in `<config>.<mode>.whitelist` if that whitelist is present; otherwise a `ConfigurationException` is thrown. Most `Properties` operations delegate directly and do not apply checks except `getProperty` and custom `iterator`.

State/persistence: wrapper holds references to mutable backing properties and crypto properties. Dependencies: Ozone config keys, Hadoop `StringUtils`, HDDS `ConfigurationException`.

Integration points: `OzoneConfiguration.getProps`, config object binding, iteration over configuration entries, crypto compliance mode. Risks: `get(Object)` bypasses compliance while `getProperty(String)` enforces it; null values may be checked against whitelist and rejected; concurrent behavior depends on backing properties; whitelist omission means any value is accepted. Test signals: restricted and unrestricted modes, whitelist allow/deny, bypass via `get`, iterator enforcement, and compliance mode key exemption.
