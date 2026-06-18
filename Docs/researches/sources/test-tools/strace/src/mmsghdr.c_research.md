<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/mmsghdr.c -->
# sources/test-tools/strace/src/mmsghdr.c

Purpose: decodes vectorized message syscalls `sendmmsg` and `recvmmsg`.
Important APIs/types/functions: `decode_mmsgvec`, `save_mmsgvec_namelen`, `print_struct_mmsghdr`, `dumpiov_in_mmsghdr`, `do_recvmmsg`, time32/time64 variants, and `msghdr.h` helpers.
Control flow: sendmmsg prints sockfd on entry and decodes message vector on exit with cleared syserror for partial sends; recvmmsg saves per-message name lengths and timeout text on entry, then prints only returned messages and timeout status on exit.
State and persistence behavior: stores per-syscall `mmsgvec_data` in `tcb` private data with a free callback. Dependencies and integration points: `msghdr.c`, iovec dump logic, and socket syscall table.
Risks: vector counts are capped by `IOV_MAX`; partial success and timeout formatting are subtle. Test signals: verbose/nonverbose sendmmsg, recvmmsg timeout, partial vectors, changed namelen, and time32/time64 tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/mmsghdr.c -->
