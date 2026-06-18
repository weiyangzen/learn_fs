# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/SafeModeWaitSubcommand.java

## Purpose
Implements `ozone admin safemode wait`, polling SCM until safe mode ends or a timeout expires.

## Important APIs, Types, And Functions
The command is a picocli `Callable<Void>` with `-t/--timeout` seconds, `ScmOption`, `Time.monotonicNow`, and `ScmClient.inSafeMode()`. `getRemainingTimeInSec()` computes timeout budget from monotonic time.

## Control Flow
`call()` records start time, opens an SCM client, loops while remaining time is positive, checks `inSafeMode`, sleeps one second between checks, and retries after `InterruptedException`. On success it prints that SCM is out of safe mode; on timeout it throws `TimeoutException`.

## State And Persistence
No persistent state is written. It repeatedly opens clients and reads SCM safe mode state.

## Dependencies And Integration Points
Depends on `ScmOption`, `ScmClient`, Hadoop `Time`, and picocli. It is registered under `SafeModeCommands`.

## Risks And Test Signals
The `InterruptedException` path sleeps and then re-interrupts, which can cause the outer loop to continue with the interrupted flag set. Tests should cover zero/short timeout, successful transition, timeout exit code, unavailable SCM retries, and interruption behavior.
