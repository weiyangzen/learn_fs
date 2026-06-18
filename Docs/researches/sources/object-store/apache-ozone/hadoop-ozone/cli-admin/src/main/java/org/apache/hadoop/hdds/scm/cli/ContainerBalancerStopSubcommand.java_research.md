# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStopSubcommand.java

Purpose: This subcommand sends a request to stop SCM's container balancer and reports the outcome to the administrator.

Important APIs and types: It extends `ScmSubcommand`, is picocli command `stop`, and calls `ScmClient.stopContainerBalancer`.

Control flow: `execute` prints that the stop command is being sent, calls the SCM client, prints `Container Balancer stopped.` on success, and on `IOException` prints a failure message to stderr before rethrowing.

State and persistence behavior: No local persistence. The command affects remote balancer runtime state in SCM.

Dependencies and integration points: It is registered under `ContainerBalancerCommands` and relies on `ScmClient` to reach SCM.

Risks: The initial message says it is waiting for the balancer to stop, but actual blocking semantics depend entirely on `ScmClient.stopContainerBalancer`. Errors are rethrown after printing, so callers receive both stderr and nonzero exit behavior.

Test signals: Client stop method invocation, success text, and stderr failure text plus propagated `IOException`.
