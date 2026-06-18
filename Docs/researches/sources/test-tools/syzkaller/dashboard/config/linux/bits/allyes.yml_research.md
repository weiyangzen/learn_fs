# sources/test-tools/syzkaller/dashboard/config/linux/bits/allyes.yml

Purpose: config fragment for broad `allyes`-style Linux builds that disables known build/boot hazards, heavyweight debugging, and self-tests to make maximally enabled kernels usable for syzbot fuzzing.

Important keys: top-level `config` list with Kconfig symbols and conditional tags. It disables problematic boot/build options such as `SERIAL_NUVOTON_MA35D1_CONSOLE`, `MAXSMP`, MSI-related drivers, `GPIB_CB7210`, numerous sanitizers/debug features, fault injection, KUnit/runtime tests, and many subsystem self-tests.

Control flow: consumed by the syzkaller dashboard config generator/merger; entries either force symbols on/off, append command-line text, or use modifiers like `[override]`. There is no executable flow in the file itself.

State and persistence: declarative only. It contributes to generated kernel `.config` output and boot command line through `CMDLINE` append.

Dependencies and integration points: Linux Kconfig symbol names across versions, base config fragments, and syzkaller's YAML config-bit parser. Comments document why specific features are disabled due to boot slowness, runtime crashes, or build failures.

Risks: symbol names age quickly; disabled lists can silently stop matching or hide coverage. Overriding sanitizers/debug/fault-injection accelerates boot but reduces bug-finding depth. The broad MSI disable block is intentionally imprecise and may mask useful drivers.

Test signals: generated allyes configs should build and boot. Failures are usually kernel build errors, boot hangs, or syzbot infrastructure timeouts.
