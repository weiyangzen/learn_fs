# sources/test-tools/ltp/testcases/kernel/syscalls/alarm/alarm03.c

Purpose: confirms alarms are not inherited across `fork()`. The parent schedules `alarm(100)`, forks, child calls `alarm(0)` and should get zero, while parent cancels and expects 100 seconds remaining. Important APIs are `alarm`, `SAFE_FORK`, and LTP expected-value macros. State is parent and child process alarm timers. Dependencies are fork semantics. Risks are small timing windows but the operations are immediate. Test signal is child has no inherited alarm and parent retains its alarm.
