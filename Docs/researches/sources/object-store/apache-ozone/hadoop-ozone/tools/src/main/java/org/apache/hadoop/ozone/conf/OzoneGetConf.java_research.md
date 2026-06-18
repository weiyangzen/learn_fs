# sources/object-store/apache-ozone/hadoop-ozone/tools/src/main/java/org/apache/hadoop/ozone/conf/OzoneGetConf.java

## Purpose
Picocli-based `ozone getconf` command for printing selected Ozone configuration values and service host lists.

## Important APIs, types, and functions
Extends `GenericCli`, exposes helper methods `printError`, `printOut`, and package-private `getConf`, and registers subcommands `PrintConfKeyCommandHandler`, `StorageContainerManagersCommandHandler`, and `OzoneManagersCommandHandler`.

## Control flow
`main` resets log4j configuration to concise console output, suppresses native-code loader noise, then executes the CLI through `GenericCli.run`.

## State and persistence behavior
Reads current `OzoneConfiguration`; does not persist or mutate config. It mutates process logging setup.

## Dependencies and integration points
Integrates HDDS `GenericCli`, picocli, `HddsVersionProvider`, `OzoneConfiguration`, and log4j/reload4j.

## Risks and edge cases
Package-private helper methods ease testing but keep command handlers tightly coupled to the parent class. Logging reset is global and can affect embedded callers.

## Test signals
`TestGetConfOptions` captures stdout for `confKey`, `storagecontainermanagers`, and `ozonemanagers` aliases.
