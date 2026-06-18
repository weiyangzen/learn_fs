# sources/test-tools/syzkaller/dashboard/config/linux/bits/android.yml

Purpose: common config bits for all Android kernels tested by syzbot.

Important keys: enables `KERNEL_GZIP`, appends Android GKI command-line settings for pressure and memory cgroups, disables `KVM_WERROR`, sets `SERIAL_8250_RUNTIME_UARTS: 4`, enables `NET_VENDOR_GOOGLE`, and overrides `BOOTPARAM_SOFTLOCKUP_PANIC`.

Control flow: declarative fragment merged after branch defconfig.

State and persistence: affects generated kernel `.config` and command line.

Dependencies and integration points: Android GKI defaults, syzbot distro package availability, qemu serial behavior, Google network drivers, and shared softlockup panic policy.

Risks: `KERNEL_GZIP` trades off compression behavior because lz4 is unavailable in syzbot distros. Serial UART count is a boot workaround that may be branch/platform-specific. Appended cgroup args must remain compatible with kernel versions.

Test signals: Android kernels build without missing lz4, boot under qemu, and retain softlockup panic behavior.
