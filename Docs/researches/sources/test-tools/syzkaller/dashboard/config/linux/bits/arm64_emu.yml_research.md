# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_emu.yml

Purpose: large ARM64 emulation-focused fragment that disables broad sets of hardware drivers and platform menus to reduce qemu boot time, build size, and irrelevant crash noise.

Important keys: top-level `config` list disables PCMCIA, display/DRM panels, SPI/MMC/PWM/RC/HWMON/regulator/watchdog/memstick/COMEDI, many platform `ARCH_*` selections, PCI controller drivers, special HID drivers, bus devices, I2C controllers, MFD drivers, camera sensors, backlight/LCD drivers, RPMSG, ADC/light/pressure sensors, PHY drivers, and additional platform-specific blocks through the end of the file.

Control flow: declarative deny-list applied after ARM64 base config. Comments group related Kconfig menu families, making the file a curated pruning layer rather than a feature-enabling profile.

State and persistence: only affects generated `.config`; no executable state.

Dependencies and integration points: ARM64 defconfig symbol names across kernel versions, qemu emulation performance constraints, syzkaller config parser, and other ARM64 fragments such as `arm64.yml`.

Risks: a huge explicit disable list is maintenance-heavy. Renamed/removed symbols can become inert, while new hardware menu symbols may reintroduce boot slowness. Disabling whole driver classes improves signal-to-noise but loses coverage for emulated/virtual devices that could be fuzzable. Some symbols are duplicated with other fragments, so override order matters.

Test signals: practical validation is ARM64 emulated kernel build and boot time, plus lower rate of unrelated platform-driver crashes. There are no direct unit tests for this YAML.
