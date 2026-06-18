# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ContainerBalancerCommands.java

Purpose: This class registers the `ozone admin containerbalancer` command group and documents container balancer usage for administrators.

Important APIs and types: It implements `AdminSubcommand`, is annotated with picocli `@Command`, uses `HddsVersionProvider`, and is registered with `@MetaInfServices(AdminSubcommand.class)`. Subcommands are `ContainerBalancerStartSubcommand`, `ContainerBalancerStopSubcommand`, and `ContainerBalancerStatusSubcommand`.

Control flow: The class has no methods. Picocli uses annotation metadata to route nested `start`, `stop`, and `status` invocations, while service-provider metadata makes the group discoverable by the admin CLI.

State and persistence behavior: No runtime state or persistence. It controls CLI registration and help text.

Dependencies and integration points: It integrates admin command discovery, picocli command hierarchy, version output, and the container balancer SCM operations implemented by child commands.

Risks: Removing `@MetaInfServices` or changing command names breaks CLI discovery or compatibility. The long help text must stay aligned with actual option names and server-side defaults.

Test signals: The admin CLI lists `containerbalancer`, routes child commands, and displays version/help metadata.
