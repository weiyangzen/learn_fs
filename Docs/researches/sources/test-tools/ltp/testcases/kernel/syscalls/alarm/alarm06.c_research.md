# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm06.c

Purpose: verifies `alarm(0)` cancels a pending alarm. Setup installs a handler; run schedules two seconds, sleeps one, cancels and expects one second remaining, then sleeps past the original expiry and expects zero signals. Important APIs are `alarm`, `sleep`, and `SAFE_SIGNAL`. State is only the process alarm timer/counter. Dependencies are POSIX signal semantics. Risks are timing sensitivity but the sleeps have margin. Test signal is cancel return value 1 and no `SIGALRM`.
