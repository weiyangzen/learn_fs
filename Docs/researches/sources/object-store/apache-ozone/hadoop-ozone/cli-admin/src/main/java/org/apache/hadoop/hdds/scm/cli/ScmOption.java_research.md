# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmOption.java

## Purpose
Provides reusable picocli options and client factories for commands that connect to SCM or SCM security services.

## Important APIs, Types, And Functions
Options are `--scm`, `--service-id`, and deprecated hidden `-id`. `createScmClient()` overloads create `ContainerOperationClient`, optionally with a supplied `OzoneConfiguration` and `ScmNodeTarget`. `checkAndSetSCMAddressArg` writes `OZONE_SCM_CLIENT_ADDRESS_KEY` and `OZONE_SCM_DEFAULT_SERVICE_ID`. `createScmSecurityClient()` delegates to `HddsServerUtil.getScmSecurityClient`.

## Control Flow
Client creation first applies command-line SCM address/service ID to configuration. If no service ID is provided or configured and no SCM client address can be derived, it throws `ConfigurationException`.

## State And Persistence
It mutates only the in-memory command configuration. The returned clients perform network RPCs but this mixin persists nothing itself.

## Dependencies And Integration Points
Integrates with Ozone configuration, `HddsUtils`, `ScmConfigKeys`, `ContainerOperationClient`, `SCMSecurityProtocol`, and SCM HA targeting.

## Risks And Test Signals
Configuration precedence and HA/non-HA validation are the core risks. Tests should cover explicit `--scm`, explicit `--service-id`, deprecated `-id`, missing non-HA address, HA default service ID behavior, and security client exception wrapping.
