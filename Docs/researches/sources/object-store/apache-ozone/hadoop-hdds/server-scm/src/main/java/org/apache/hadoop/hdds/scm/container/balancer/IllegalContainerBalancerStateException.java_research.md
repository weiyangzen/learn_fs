# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/IllegalContainerBalancerStateException.java

Purpose: domain exception for invalid Container Balancer state transitions.

Important APIs: no-arg and message constructors, extending `SCMServiceException`.

Control flow and state: carries only exception message/cause state inherited from the superclass. No persistence or side effects.

Dependencies and integration: thrown by balancer service lifecycle/control code when an operation such as start, stop, or configuration update is illegal for the current state.

Risks: no cause constructor, so call sites that catch a lower-level cause cannot preserve it directly. Test signals are mostly service-level: invalid lifecycle transitions should assert this specific exception type and useful message text.
