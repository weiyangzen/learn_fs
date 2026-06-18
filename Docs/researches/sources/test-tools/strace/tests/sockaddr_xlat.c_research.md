# sources/test-tools/strace/tests/sockaddr_xlat.c

Purpose: Standalone or shared strace regression test for socket address/option decoder. The program intentionally calls kernel interfaces with valid, invalid, edge, and faulting arguments, then prints the expected trace line so the strace test harness can compare decoder output.

Important APIs/types/functions: Visible local functions are `check_ll`, `check_in`, `validate_in6`, `check_in6`, `check_tipc`, `check_sco`, `check_rc`, `check_rxrpc`, `check_ieee802154`, `check_alg`, `check_nfc`, `check_vsock`, plus 4 more. Important syscall/test APIs and data types are `socket`, `connect`, `getsockopt`, `setsockopt`, `sockaddr`, `cmsghdr`, `sockaddr decoding`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `tail_alloc`, `XLAT_RAW/ABBREV/VERBOSE`, `printxval/printflags`. Preprocessor knobs/macros are `IEEE802154_ADDR_LEN=8`, `IEEE802154_PANID_BROADCAST=0xffff`, `IEEE802154_ADDR_BROADCAST=0xffff`, `IEEE802154_ADDR_UNDEF=0xfffe`, `CRYPTO_ALG_KERN_DRIVER_ONLY=0x1000`, `SVM_FLAGS=svm_flags`, `SVM_ZERO=svm_zero`, `SVM_ZERO_FIRST=svm_zero[0]`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `FD0_PATH=""`, plus 1 more. The file has 1267 source lines and was read from `sources/test-tools/strace/tests/sockaddr_xlat.c`.

Control flow: `main` and helpers (`check_ll`, `check_in`, `validate_in6`, `check_in6`, `check_tipc`, `check_sco`, `check_rc`, `check_rxrpc`, `check_ieee802154`, `check_alg`, plus 6 more) allocate tail-guarded objects, prepare syscall/socket/signal data, invoke the kernel API, capture `sprintrc` results, and print expected trace lines. The file contains 13 explicit `for` loops and 1 visible conditionals, so coverage is table-driven where the ABI has many enum/flag combinations. It is a broad socket-address xlat test using `connect(-1, ...)` against AF_PACKET, IPv4, IPv6, TIPC, Bluetooth, RXRPC, IEEE802154, AF_ALG, NFC, VSOCK, QRTR, XDP, and MCTP structures.

State and persistence behavior: transient `errstr` caches `sprintrc` output after each syscall; tail-allocated memory creates readable and faulting boundary cases.

Dependencies: Direct dependencies are `tests.h`, `stdio.h`, `sys/socket.h`, `arpa/inet.h`, `netinet/in.h`, `linux/ax25.h`, `linux/if_arp.h`, `linux/if_ether.h`, `linux/if_packet.h`, `linux/mctp.h`, `linux/tipc.h`, `bluetooth/bluetooth.h`, plus 13 more. Integration relies on strace's `tests.h` helpers, generated `scno.h` syscall numbers, xlat tables where present, and the Makefile/test-driver entry for this source.

Integration points: The file contributes expected-output coverage for strace's decoder tests under `sources/test-tools/strace/tests`. It is normally built as a test binary or included by a macro variant, then run under strace so each printed line mirrors the decoder output for the exercised syscall family.

Risks: raw/abbrev/verbose xlat mode expectations must stay aligned with decoder tables; fault-address tests depend on tail allocation and pointer-width behavior; feature guards must skip cleanly on kernels/libcs without the ABI; socket option/address constants vary by kernel headers and architecture.

Test signals: successful self-test prints `+++ exited with 0 +++`; xlat mode variants validate raw, abbreviated, and verbose representations.
