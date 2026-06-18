## sources/object-store/apache-ozone/hadoop-ozone/fault-injection-test/pom.xml

Purpose: Maven aggregator for Apache Ozone fault-injection test modules.

Important APIs/types/functions: POM inherits from root `org.apache.ozone:ozone:2.3.0-SNAPSHOT`, has artifactId `ozone-fault-injection-test`, packaging `pom`, and declares modules `mini-chaos-tests` and `network-tests`.

Control flow: Maven builds this as an aggregator; module ordering lets the reactor include both fault-injection suites under the parent.

State and persistence behavior: no runtime state; build metadata only.

Dependencies and integration points: root Ozone parent supplies versions, plugins, and profiles. The network tests module contains the blockade tests researched in this group.

Risks: aggregator has no direct dependencies or plugin overrides, so parent POM changes can alter behavior. Module paths must remain accurate.

Test signals: `mvn` reactor selection or parent build should include both modules; missing module directories would fail project loading.
