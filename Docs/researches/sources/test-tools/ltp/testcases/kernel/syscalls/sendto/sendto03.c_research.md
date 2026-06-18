<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto03.c

Purpose: CVE-2020-14386 Check for vulnerability in tpacket_rcv() which allows an unprivileged user to write arbitrary data to a memory area outside the allocated packet buffer. Kernel crash fixed in 5.9 acf69c946233 ("net/packet: fix overflow in tpacket_rcv") In this shard it contributes focused coverage for sendto socket error, SCTP, packet socket, and overflow regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `check_tiny_frame`, `check_vnet_hdr`, `run`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_IOCTL`, `SAFE_SENDTO`, `SAFE_SETSOCKOPT_INT`, `SAFE_SOCKET`, `SAFE_SYSCONF`, `TEST`, `TST_ERR`, `TST_RET`, `TST_SR_SKIP`, `TST_TAINT_D`, `TST_TAINT_W`, `setsockopt`, `setup`, `tst_brk`, `tst_net`, `tst_path_val`, `tst_res`, `tst_setup_netns`, `tst_tag`, `tst_taint_check`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `check_tiny_frame`, `check_vnet_hdr`, `run`, `cleanup`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on LTP network helpers, kernel config gating. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto03.c -->
