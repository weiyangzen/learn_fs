# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerStatusSubcommand.java

Purpose: This subcommand reports whether the container balancer is running and, in verbose mode, prints configuration, current iteration statistics, and optional iteration history.

Important APIs and types: It extends `ScmSubcommand`, calls `ScmClient.getContainerBalancerStatusInfo`, and formats `ContainerBalancerStatusInfoResponseProto`, `ContainerBalancerStatusInfoProto`, `HddsProtos.ContainerBalancerConfigurationProto`, and `ContainerBalancerTaskIterationStatusInfoProto`. It uses `DurationUtil.getPrettyDuration`, Hadoop `StringUtils.byteDesc`, `OzoneConsts.GB`, and Java time formatting.

Control flow: `execute` prints running/not-running. When running and `isVerbose()` is true, it formats start time in the system zone, computes duration to now, prints configuration, finds the current iteration as the first status entry with empty `iterationResult`, and prints it or `-`. With `--history`, it also prints completed iterations whose result is nonempty.

State and persistence behavior: The command reads balancer status from SCM and writes formatted text. No local state is persisted.

Dependencies and integration points: It integrates CLI verbose handling, SCM balancer status protocol, byte/duration formatting utilities, and administrator-facing status output.

Risks: Output formatting is column-width based and may be brittle for tests or parsing. `Duration.between(startedAtInstant, OffsetDateTime.now())` mixes instant and offset temporal types but works through temporal conversion. Current iteration detection assumes empty result means active.

Test signals: Expected output for running/not-running, configuration values converted to GB/minutes, current iteration info, history filtering, and placeholder `-` for absent lists or no active iteration.
