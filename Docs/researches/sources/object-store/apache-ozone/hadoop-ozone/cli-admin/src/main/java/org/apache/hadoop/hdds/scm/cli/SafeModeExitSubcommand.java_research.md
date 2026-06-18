# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeExitSubcommand.java

## Purpose
Implements `ozone admin safemode exit`, a forced SCM safe mode exit operation.

## Important APIs, Types, And Functions
The class extends `ScmSubcommand` and implements `execute(ScmClient)`. It calls `scmClient.forceExitSafeMode()` and prints a success message only when the RPC returns true.

## Control Flow
`ScmSubcommand.call()` creates and closes the SCM client, then invokes `execute`. Any `IOException` from the force-exit RPC propagates through the CLI framework.

## State And Persistence
No local state is persisted. The command changes persistent cluster/SCM behavior by forcing safe mode off on the target SCM.

## Dependencies And Integration Points
Depends on `ScmClient.forceExitSafeMode`, `ScmSubcommand`, and picocli metadata. It shares address/service selection through `ScmOption` inherited by `ScmSubcommand`.

## Risks And Test Signals
This is an operationally risky command because it overrides normal safe mode rules. Tests should verify the RPC is invoked once, false return does not print a misleading success line, and failures produce a non-zero CLI result.
