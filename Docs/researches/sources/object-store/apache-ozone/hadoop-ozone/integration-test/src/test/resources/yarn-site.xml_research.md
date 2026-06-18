# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/yarn-site.xml

Purpose: This is an integration-test `yarn-site.xml` placeholder. It declares an empty Hadoop `configuration` element with the standard configuration stylesheet PI, letting tests include a YARN site resource without overriding any properties.

Important APIs/types/functions: No code APIs are defined. The effective contract is the Hadoop XML configuration schema: a root `<configuration>` element with zero `<property>` children.

Control flow, state, and persistence: The file contributes no runtime state by itself. Hadoop configuration loading can merge it into an `OzoneConfiguration`/Hadoop `Configuration`; because it is empty, it preserves defaults and only satisfies classpath/resource expectations.

Dependencies and integration points: Integrated through Hadoop's configuration resource loader in integration tests. It depends on the standard `configuration.xsl` reference only for display tooling.

Risks: Adding properties here would globally affect integration tests that load YARN resources, possibly changing scheduler, resource-manager, or mini-cluster behavior. The current empty file has low behavioral risk but can mask missing test-specific configuration if a test assumes YARN is configured.

Test signals: Presence of the file is itself a test fixture signal. No direct unit tests are defined in this file.
