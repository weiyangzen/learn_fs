<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mq.c -->
# sources/test-tools/strace/src/mq.c

Purpose: decodes POSIX message queue syscalls.
Important APIs/types/functions: `mq_open`, `do_mq_timedsend`, time32/time64 send/receive variants, `mq_notify`, `mq_getsetattr`, `printmqattr`, `print_timespec*`, and fd/path helpers.
Control flow: `mq_open` conditionally prints mode/attr for `O_CREAT`; timed send prints message bytes and timeout on entry; timed receive prints buffer and priority on exit but timeout as entry-read data; notify and getsetattr print sigevent/attributes according to syscall phase.
State and persistence behavior: no persistent state beyond syscall phase. Dependencies and integration points: mqueue syscall table and time64 compatibility. Risks: receive buffer length is return-value bounded; timeout must print even on failure. Test signals: create/no-create open, send/receive success/error, priority pointer failures, notify, and getsetattr tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mq.c -->
