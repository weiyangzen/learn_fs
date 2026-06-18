<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp.c -->
# sources/test-tools/strace/tests/ioctl_ptp.c

Purpose: comprehensive PTP clock ioctl decoder test covering capabilities, external timestamp, periodic output, PPS, system offset, pin functions, precise timestamps, extended timestamps, unknown commands, xlat modes, and injected success.

Important APIs/types/functions: Uses `sys_ioctl`, `print_lltime`, `check_bad_ptr`, `test_no_device`, PTP structs `ptp_clock_caps`, `ptp_sys_offset`, `ptp_sys_offset_extended`, `ptp_sys_offset_precise`, `ptp_extts_request`, `ptp_perout_request`, `ptp_pin_desc`, and xlat tables for external timestamp flags, periodic output flags, pin functions, and clock ids.

Control flow: optional injection lock loops on `PTP_CLOCK_GETCAPS`. `test_no_device` sweeps unknown PTP command numbers and directions, probes NULL/bad pointers, then exercises `PTP_CLOCK_GETCAPS{,2}`, `PTP_EXTTS_REQUEST{,2}`, `PTP_PEROUT_REQUEST{,2}`, `PTP_ENABLE_PPS{,2}`, `PTP_SYS_OFFSET{,2}`, `PTP_PIN_[GS]ETFUNC{,2}`, `PTP_SYS_OFFSET_PRECISE{,2,_CYCLES}`, and `PTP_SYS_OFFSET_EXTENDED{,2,_CYCLES}` with crafted timestamps, flags, reservations, and truncation boundaries.

State and persistence behavior: all state is allocated test structs; fd `-1` avoids device state. Injected mode simulates successful output fields and before/after decoding.

Dependencies/integration points: depends on `linux/ptp_clock.h`, xlat tables, time formatting helpers, xlat mode macros, and syscall injection.

Risks and test signals: time-width differences, header versions, reserved-field policies, and xlat modes create many expected-output variants. Passing output confirms PTP command recognition, nested timestamp formatting, array truncation, flags/enums, pointer handling, and success/error direction behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ptp.c -->
