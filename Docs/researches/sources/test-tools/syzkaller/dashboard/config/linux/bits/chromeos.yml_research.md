# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos.yml

Purpose: common config bits for all ChromeOS kernels.

Important keys: disables `SECURITY_CHROMIUMOS_NO_UNPRIVILEGED_UNSAFE_MOUNTS`, appends ChromeOS boot command-line flags, disables several cros_ec sensor drivers due to build warnings, sets `FRAME_WARN: 0`, and overrides `BOOTPARAM_SOFTLOCKUP_PANIC`.

Control flow: declarative fragment layered on ChromeOS branch configs.

State and persistence: affects generated `.config` and command line.

Dependencies and integration points: ChromeOS-specific security options, syzkaller executor mount setup, ChromeOS EC sensor drivers, and softlockup panic policy.

Risks: disabling ChromeOS unprivileged mount protection is necessary for executor setup but changes security posture. Historical command-line flags have unclear origins and may need pruning. Sensor build warnings may be fixed in later branches, so disables can hide coverage.

Test signals: ChromeOS kernels should permit syzkaller tmpfs mounts, build without the noted cros_ec fallthrough errors, and boot with expected softlockup behavior.
