# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOzoneConfigurationFields.java

## Purpose
`TestOzoneConfigurationFields` enforces consistency between Java configuration constants and `ozone-default.xml`. It extends Hadoop's `TestConfigurationFieldsBase` and declares the Ozone, SCM, HDDS, Recon, S3 gateway, and S3 secret config classes whose public config constants should be represented in the XML defaults, while maintaining explicit skip lists for dynamic, deprecated, tested-elsewhere, or intentionally non-XML properties.

## Important APIs, Types, and Functions
- `initializeMemberVariables` sets `xmlFilename`, `configurationClasses`, `errorIfMissingConfigProps`, and `errorIfMissingXmlProps`.
- `xmlPropsToSkipCompare`, `xmlPrefixToSkipCompare`, `configurationPropsToSkipCompare`, and `configurationPrefixToSkipCompare` are inherited mutable sets that define exceptions.
- `addPropertiesNotInXml` centralizes the larger skip list for keys that are intentionally not documented in `ozone-default.xml`.
- Config classes include `OzoneConfigKeys`, `ScmConfigKeys`, `OMConfigKeys`, `HddsConfigKeys`, Recon keys, S3 gateway keys, and S3 secret keys.

## Control Flow
The test framework calls `initializeMemberVariables`, after which the inherited base test reflects over the listed classes and compares discovered property names with the XML file. The method first enables strict missing-property checks, then adds specific XML examples and prefixes to skip, excludes known client-side/default fields and deprecated values, skips Ranger prefixes pending finalization, and invokes `addPropertiesNotInXml` for generated, HA-template, internal, test-only, or otherwise non-defaulted keys.

## State and Persistence Behavior
There is no runtime service state or persistence. The file mutates inherited test configuration collections before the base-class comparison executes.

## Dependencies and Integration Points
The file integrates with `ozone-default.xml`, Java config-key classes across Ozone/HDDS/Recon/S3 packages, and `HttpServer2.HTTP_IDLE_TIMEOUT_MS_KEY`, which is excluded because another test owns it. It is a documentation/configuration contract test rather than a service behavior test.

## Risks and Edge Cases
The skip lists can hide real documentation gaps if keys remain there after becoming user-facing. There is a duplicate skip for `ozone.scm.nodes.EXAMPLESCMSERVICEID`. Strict `errorIfMissingConfigProps` and `errorIfMissingXmlProps` make the test sensitive to both new Java constants and stale XML properties, which is intentional but can cause broad failures during config refactors.

## Test Signals
Passing means the configured key classes and `ozone-default.xml` are synchronized except for documented exceptions. Failures are strong signals that a new config key lacks XML documentation, an XML property lacks a matching constant, or an exception list needs deliberate review.
