# sources/object-store/apache-ozone/hadoop-ozone/multitenancy-ranger/pom.xml

## Purpose

This Maven POM defines the `ozone-multitenancy-ranger` JAR module, the Ranger-backed implementation of Ozone Manager multitenancy integration.

## Important APIs and Types

The artifact is `org.apache.ozone:ozone-multitenancy-ranger:2.3.0-SNAPSHOT` with parent `org.apache.ozone:ozone`. It packages a JAR and names the module "Apache Ozone Multitenancy with Ranger".

## Control Flow

Build flow is standard Maven. The compiler plugin disables annotation processing with `<proc>none</proc>`. SpotBugs is configured with the module-local exclude file. Runtime dependencies include Jersey client and Ranger integration/client libraries. Provided dependencies link the module back to Hadoop/Ozone manager APIs. Test dependencies include Hadoop auth/common test jars and Ozone/HDDS test utilities.

## State and Persistence

The POM controls dependency graph and plugin state, not application state. It intentionally sets `classpath.skip` to `false`.

## Dependencies and Integration Points

The main integrations are `ranger-intg`, `ranger-plugins-common`, `jersey-client`, `hadoop-common`, `hdds-common`, `hdds-config`, `ozone-common`, and `ozone-manager`. The POM excludes many transitive artifacts from `ranger-plugins-common`, including logback, AWS/GCS connectors, Hadoop client bundles, Hive, Kafka, Lucene/Solr, Elasticsearch/OpenSearch, Jersey bundle, commons-logging, JAXB/activation, and JSON-smart, mostly to avoid classpath bloat and binding conflicts.

## Risks and Edge Cases

Ranger dependencies often pull broad transitive graphs; the exclusions are important and can break if Ranger changes artifact structure. Disabling annotation processing is appropriate for this adapter but means generated config/validator processors from OM are not run here. Provided scope requires the host Ozone distribution to supply matching Ozone/Hadoop classes.

## Test Signals

Module compile, dependency convergence/enforcer checks, SpotBugs, and the Ranger integration test class are the build signals. Because Ranger endpoint tests are marked unhealthy/manual, routine CI likely verifies mostly compilation and static analysis.
