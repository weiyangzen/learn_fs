# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_gce.yml

Purpose: ARM64 GCE pruning fragment that disables noisy or unsupported drivers/platforms to make cloud ARM64 fuzzing practical.

Important keys: disables sound, several DRM/GPU drivers, Hisilicon networking, storage filesystems/drivers, many ARM64 platform `ARCH_*` selections, remaining clock drivers, camera/video, Mellanox/Intel networking, Atheros WLAN, and selects size optimization over performance.

Control flow: declarative config list layered on ARM64 GCE builds.

State and persistence: affects generated `.config` only.

Dependencies and integration points: ARM64 GCE manager configs, Linux platform Kconfig menus, and shared ARM64 fragment that excludes some vexpress-only symbols when `arm64_gce` tag is present.

Risks: disabling broad vendor/platform support can hide bugs in cloud-available hardware paths if assumptions change. `CC_OPTIMIZE_FOR_SIZE` may alter compiler behavior and coverage/performance tradeoffs. Symbol list needs periodic refresh as ARM64 platforms are added.

Test signals: ARM64 GCE kernels should build, boot, and avoid known irrelevant platform-driver failures.
