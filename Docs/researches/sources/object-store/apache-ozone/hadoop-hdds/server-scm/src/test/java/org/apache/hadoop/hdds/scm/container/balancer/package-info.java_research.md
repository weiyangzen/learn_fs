# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/package-info.java

Purpose: This package descriptor documents that the package contains unit tests for `org.apache.hadoop.hdds.scm.container.balancer.ContainerBalancer`.

Important APIs and types: It contains only Javadoc and the package declaration `org.apache.hadoop.hdds.scm.container.balancer`; the Javadoc links to the production `ContainerBalancer` class.

Control flow: There is no executable control flow.

State and persistence behavior: There is no runtime state or persistence.

Dependencies and integration points: The file is a Java package-info artifact used by Javadoc and Checkstyle/package documentation rules. It aligns the balancer test package with the production container balancer API.

Risks: The only practical risk is stale documentation if the package scope grows beyond `ContainerBalancer` tests or if the linked production class is renamed.

Test signals: Compilation and Checkstyle/package documentation validation are the only signals.
