# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64.yml

Purpose: common ARM64 config fragment for syzbot.

Important keys: optional shell defconfig/kvm guest commands gated by `[-nodefconfig]`, command-line root/console settings, command-line source compatibility symbols across versions, ARM64 features `TAGGED_ADDR_ABI`, `PMEM`, `MTE`, and vexpress clock/platform symbols disabled for `arm64_gce`.

Control flow: establishes defconfig unless `nodefconfig` tag is set, then applies config entries with version/platform guards.

State and persistence: affects generated ARM64 `.config` and boot command line.

Dependencies and integration points: ARM64 qemu/GCE platforms, kernel command-line Kconfig symbol history, and memory-tagging coverage.

Risks: command-line symbol changes (`CMDLINE_EXTEND`, `CMDLINE_FROM_BOOTLOADER`) are version-sensitive. Enabling MTE/tagged address support changes syscall/runtime behavior and requires compatible hardware/emulation.

Test signals: ARM64 configs should build and boot on both emulated and GCE variants, with expected command-line handling.
