# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/ScmSubcommand.java

## Purpose
Defines the base class for SCM admin subcommands that need an `ScmClient`.

## Important APIs, Types, And Functions
`ScmSubcommand` extends `AbstractSubcommand` and implements `Callable<Void>`. It mixes in `ScmOption`, declares abstract `execute(ScmClient)`, and finalizes `call()` to create, use, and close a client.

## Control Flow
Picocli invokes `call`; the base class opens a client via `scmOption.createScmClient()`, calls subclass `execute`, and closes the client using try-with-resources.

## State And Persistence
No state is stored beyond the injected options. State changes are entirely in subclass RPCs.

## Dependencies And Integration Points
Used by most SCM command implementations in this work item: safe mode exit, topology, container, datanode, and pipeline commands.

## Risks And Test Signals
The final `call()` makes subclass execution simple but prevents subclasses from owning custom client lifecycle unless they do not extend it. Tests should verify clients are closed on success and exception and that subclass IOExceptions propagate.
