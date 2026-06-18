<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc.c -->
# sources/test-tools/strace/tests/ioctl_rtc.c

Purpose: comprehensive RTC ioctl decoder test covering no-argument commands, scalar/pointer long commands, time/alarm/wake alarm structs, PLL info, voltage-low flags, NVRAM alias, and generic `RTC_PARAM_{GET,SET}`.

Important APIs/types/functions: Uses `do_ioctl`, `do_ioctl_ptr`, `skip_ioctls`, `print_rtc_time`, `linux/rtc.h`, fallback `struct rtc_param`, `RTC_AIE_*`, `RTC_PIE_*`, `RTC_UIE_*`, `RTC_WIE_*`, `RTC_EPOCH_*`, `RTC_IRQP_*`, `RTC_ALM_*`, `RTC_RD_TIME`, `RTC_SET_TIME`, `RTC_WKALM_*`, `RTC_PLL_*`, `RTC_VL_*`, and `RTC_PARAM_*`.

Control flow: optional injection locks on `RTC_AIE_OFF`. The main path iterates no-arg, scalar, pointer-long, and pointer command arrays; probes NULL and EFAULT-style pointers; fills and prints `rtc_time`, `rtc_wkalrm`, and `rtc_pll_info`; tests voltage-low flag combinations; emits `NVRAM_INIT`; then runs `RTC_PARAM_GET/SET` with crafted params for features, correction, backup switch mode, and unknown params.

State and persistence behavior: local test buffers only. Invalid fd prevents RTC device changes; injection enables successful read-output forms.

Dependencies/integration points: depends on RTC UAPI, feature/backup-switch xlat tables, verbose macro, and syscall injection.

Risks and test signals: newer RTC params and feature bits vary by headers. Passing output confirms direction-aware RTC struct decoding, verbose time formatting, feature/flag xlat handling, and unknown param fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_rtc.c -->
