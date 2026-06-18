<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd.c -->
# sources/test-tools/strace/tests/ioctl_mtd.c

Purpose: tests Memory Technology Device ioctl decoding across info, erase, OOB, region, OTP, ECC, bad-block, and 64-bit variants.

Important APIs/types/functions: Uses `do_ioctl`/`do_ioctl_ptr`, `mtd/mtd-abi.h`, `linux/ioctl.h`, MTD structs such as `mtd_info_user`, `erase_info_user`, `erase_info_user64`, `mtd_oob_buf`, `mtd_oob_buf64`, `region_info_user`, `otp_info`, `mtd_write_req`, and command constants like `MEMGETINFO`, `MEMERASE`, `MEMREADOOB`, `MEMWRITEOOB`, `MEMGETREGIONINFO`, `OTP*`, `ECCGET*`, and `MEMWRITE`.

Control flow: optional injection lock is followed by null/bad-pointer probes, crafted struct calls for read/write commands, scalar offset tests for bad-block operations, region/OTP arrays, ECC statistics/layout, and fallback unknown command decoding. The file uses helper arrays to cover known and unknown enum/flag combinations.

State and persistence behavior: all state is local test memory. Invalid fd prevents real flash operations; injected success enables output-buffer decoding.

Dependencies/integration points: depends on MTD UAPI availability, strace xlat tables, Linux version conditionals for newer commands, and syscall injection.

Risks and test signals: header-version variability and command aliases can affect expected strings. Passing output confirms direction-aware MTD struct decoding, 64-bit field handling, enum/flag expansion, and pointer fallback behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_mtd.c -->
