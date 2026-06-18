<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.h -->
# sources/test-tools/strace/src/msghdr.h

Purpose: declares msghdr/mmsghdr fetch and print helpers shared by socket message decoders.
Important APIs/types/functions: `struct msghdr`, `struct mmsghdr` fetch wrappers, `sizeof_struct_mmsghdr`, `print_struct_msghdr`, `dumpiov_in_msghdr`, and `dumpiov_in_mmsghdr` declarations.
Control flow: header only; implementation is split between `msghdr.c` and `mmsghdr.c`. State and persistence behavior: no state.
Dependencies and integration points: `sendmsg`, `recvmsg`, `sendmmsg`, and `recvmmsg` decoders. Risks: prototypes must match mpers/native structure fetch implementations. Test signals: compile coverage and socket message syscall tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/msghdr.h -->
