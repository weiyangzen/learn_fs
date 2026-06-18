<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestContainerBalancerSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestContainerBalancerSubCommand.java

Purpose: Tests container balancer CLI status, verbose/history output, start, and stop behavior against a mocked SCM client.

Important APIs and types: `ContainerBalancerStatusSubcommand`, `ContainerBalancerStartSubcommand`, `ContainerBalancerStopSubcommand`, `ContainerBalancerStatusInfoResponseProto`, `ContainerBalancerTaskIterationStatusInfo`, `ContainerBalancerConfiguration`, `IterationInfo`, regex patterns for output, Mockito, and AssertJ.

Control flow: Helpers build status response protos with running/stopped state, iteration history, balancing stats, and configuration. Tests execute status without flags, verbose history, verbose current output, stopped balancer status, stop success/failure, start success, and start failure when already running. Output is captured through helper stream suppliers and matched with patterns.

State and persistence behavior: No persistence. Mocked SCM client responses model the balancer's in-memory service status and configuration. Start/stop state changes are represented by mocked RPC returns or thrown IOExceptions.

Dependencies and integration points: Exercises CLI formatting over SCM container balancer service APIs and validates configuration display for balancing thresholds, move limits, data sizes, and duration values.

Risks: Many assertions are regex-based and sensitive to wording. Time/duration formatting must remain stable. Start and stop tests focus on user-visible output rather than verifying every configuration field sent to SCM.

Test signals: `Container Balancer is Running/Not Running`, started-at and duration fields, verbose iteration stats/history, stop waiting message, failed stop stderr, start success text, and failed start exception/message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/datanode/TestContainerBalancerSubCommand.java -->
