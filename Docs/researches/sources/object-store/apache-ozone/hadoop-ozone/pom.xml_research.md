<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/pom.xml

## Purpose
Top-level Apache Ozone Maven aggregator.

## Important APIs, types, and functions
Declares artifact `ozone` with packaging `pom`, lists core modules including clients, OM, datanode, recon, ozonefs, and gateway modules, configures jar/test-jar exclusions for web/node assets, and processes remote resource bundles. Profiles add `iceberg`, shaded Ozone filesystem modules, go-offline modules, and parallel-test surefire settings.

## Control flow
Default build includes standard modules. The `build-with-ozonefs` profile activates when `skipShade` is not set and adds `ozonefs-hadoop2`, `ozonefs-hadoop3`, and `ozonefs-shaded`. Parallel test profile adjusts fork directories and system properties.

## State and persistence behavior
Defines Maven build graph and generated build outputs only.

## Dependencies and integration points
This file determines when filesystem compatibility modules and recon codegen participate in the overall Ozone build.

## Risks and test signals
Profile activation errors can omit release-critical filesystem artifacts. Parallel-test configuration changes can cause test workspace collisions. Signals are full Maven reactor builds under default, `skipShade`, go-offline, JDK 11+, and parallel-test profiles.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/pom.xml -->
