# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/InvalidContainerBalancerConfigurationException.java

Purpose: domain exception for invalid `ContainerBalancerConfiguration` values.

Important APIs: no-arg constructor, message constructor, and message plus `IOException` cause constructor, all extending `SCMServiceException`.

Control flow and state: pure exception wrapper with inherited message/cause persistence. The IOException constructor supports configuration parsing failures while preserving the original IO problem.

Dependencies and integration: used by configuration validation and balancer service startup/update paths.

Risks: cause constructor is specialized to `IOException`, so non-IO validation causes cannot be preserved without wrapping elsewhere. Test signals should assert invalid threshold, size, timeout, and file parsing paths fail with this type and include actionable messages.
