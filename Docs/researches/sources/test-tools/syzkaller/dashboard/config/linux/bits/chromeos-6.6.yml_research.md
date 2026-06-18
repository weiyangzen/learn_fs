# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.6.yml

Purpose: ChromeOS 6.6 kernel source selector with io_uring enabled.

Important keys: ChromiumOS kernel repo, tag `3f6e68d242bb045866ae04a9f5890aacd987d2bb`, ChromeOS prepareconfig command, `make olddefconfig`, and `IO_URING`.

Control flow: declarative checkout and shell preparation, then config merge.

State and persistence: generated config input only.

Dependencies and integration points: ChromeOS 6.6 tree, prepareconfig, io_uring fuzzing coverage.

Risks: pinned tag freshness and branch-specific io_uring stability. Explicit enablement may conflict with future branch defaults.

Test signals: successful build/boot and io_uring availability on ChromeOS 6.6 managers.
