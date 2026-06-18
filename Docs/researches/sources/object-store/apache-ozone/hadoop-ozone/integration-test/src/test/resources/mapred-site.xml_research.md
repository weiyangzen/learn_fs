# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/mapred-site.xml

Purpose: This placeholder `mapred-site.xml` exists on the integration-test classpath for MapReduce configuration compatibility.

Important APIs and types: It is an XML `<configuration>` with no properties.

Control flow: There is no executable flow.

State and persistence behavior: Static empty configuration only.

Dependencies and integration points: Hadoop MapReduce and DistCp tests may load `mapred-site.xml`; this file supplies a no-op resource so defaults or programmatic settings control behavior. For example, `AbstractContractDistCpTest` sets local job tracker configuration programmatically rather than through this file.

Risks: Tests requiring MapReduce-specific overrides must not assume this file provides them.

Test signals: None directly, other than resource availability and absence of mapred overrides.
