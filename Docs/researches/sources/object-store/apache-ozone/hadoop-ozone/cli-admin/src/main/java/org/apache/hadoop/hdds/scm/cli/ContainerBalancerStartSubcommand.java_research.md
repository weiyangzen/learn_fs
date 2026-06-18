# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStartSubcommand.java

Purpose: This subcommand starts SCM's container balancer with optional runtime configuration overrides supplied from the command line.

Important APIs and types: It extends `ScmSubcommand`, is annotated as picocli command `start`, accepts many `Optional` options, and calls `ScmClient.startContainerBalancer`. It consumes `StartContainerBalancerResponseProto`.

Control flow: Picocli populates option fields for threshold, iterations, max datanodes involved, move-size limits, iteration interval, move timeouts, network topology flag, include/exclude datanodes, and include/exclude containers. `execute` passes all optionals to the SCM client. If the response has `start=true`, it prints success. Otherwise it prints failure, optional reason, and throws `IOException`.

State and persistence behavior: The command itself persists no state. It sends desired balancer configuration to SCM, where balancer runtime state is controlled.

Dependencies and integration points: It maps CLI syntax to `ScmClient` and SCM protocol `StartContainerBalancerResponseProto`. Option aliases preserve older camelCase names for compatibility.

Risks: Option validation is largely delegated to server-side handling; invalid values may reach SCM. Include/exclude lists are raw comma-separated strings. Failure throws after printing to stderr, which affects CLI exit behavior.

Test signals: Successful response prints `Container Balancer started successfully.` Failed response prints failure and reason and raises `IOException`; client method receives all optionals in the documented order.
