# sources/user-network-fs/libsmb2/include/picow/lwipopts.h

## Purpose
`lwipopts.h` provides Pico W lwIP configuration overlays for libsmb2 examples.

## Important APIs, Types, and Functions
It includes `lwipopts_examples_common.h`, enables `LWIP_SO_RCVBUF`, and sets `LWIP_TIMEVAL_PRIVATE` to `0`. When `NO_SYS` is false, it defines TCP/IP and default thread stack sizes, mailbox sizes, and `LWIP_TCPIP_CORE_LOCKING_INPUT`.

## Control Flow
There is no runtime control flow in this header. lwIP compiles socket, mailbox, and thread behavior based on these macros.

## State and Persistence Behavior
Runtime lwIP state sizes are affected through receive buffers, mailboxes, and TCP/IP thread stack settings. No persistent storage is used.

## Dependencies and Integration Points
It depends on the common Pico lwIP options header and integrates with FreeRTOS or bare-metal Pico W network builds. `LWIP_TIMEVAL_PRIVATE 0` avoids conflicts with system timeval definitions expected by libsmb2.

## Risks and Edge Cases
Small 1024-byte thread stacks and mailbox sizes of 8 can limit heavy SMB transfers. Option behavior changes depending on `NO_SYS`, so builds must ensure intended socket/thread mode.

## Test Signals
Build with both polling and non-polling Pico networking modes, run sustained SMB reads/writes, and observe receive buffer/mailbox exhaustion or stack growth.
