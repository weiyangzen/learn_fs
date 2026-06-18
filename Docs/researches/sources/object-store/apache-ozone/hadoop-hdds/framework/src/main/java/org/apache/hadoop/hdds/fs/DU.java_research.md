# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/fs/DU.java

## Purpose

`DU` implements `SpaceUsageSource` using the Unix `du -sk` command. It provides accurate directory usage for datanode volumes, optionally excluding paths.

## Important APIs, Types, and Functions

Constructors accept a `File`, an optional exclude pattern, or a `Supplier<File>` exclusion provider. `getUsedSpace()` delegates to the inner `DUShell`. `constructCommand` handles Linux `--exclude` versus macOS `-I`.

## Control Flow

`DUShell.getUsed()` runs the shell command and parses the first output line. `parseExecResult` splits by tab, parses kilobytes, and converts to bytes using `OzoneConsts.KB`. Dynamic exclusion providers are evaluated each command execution.

## State and Persistence Behavior

The object stores command templates and an atomic last parsed value. It does not persist; persistence is supplied by `SaveSpaceUsageToFile`.

## Dependencies and Integration Points

It extends `AbstractSpaceUsageSource`, uses Hadoop `Shell`, and feeds `DUFactory`/`DUOptimized`.

## Risks and Test Signals

It requires a compatible platform `du`; malformed output or nonzero exits become `UncheckedIOException`. Exclude behavior differs by OS. Tests should mock shell output, verify byte conversion, exercise static and dynamic exclusions, and cover command failure paths.
