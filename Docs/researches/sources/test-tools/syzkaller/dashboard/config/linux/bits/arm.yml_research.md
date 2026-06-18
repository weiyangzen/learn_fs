# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm.yml

Purpose: ARM32 kernel config fragment for syzbot, selecting vexpress/kvm guest defaults and enabling ARM-specific coverage while avoiding known boot/parser hazards.

Important keys: shell runs `make vexpress_defconfig` and `make kvm_guest.config`. Config appends root/console/vmalloc command line, enables `ARM_LPAE`, frame-pointer unwinder, verbose backtraces, highmem options, big.LITTLE/NEON/VFP, flat binary formats, selected device drivers, and disables `HARDEN_BRANCH_PREDICTOR`.

Control flow: shell commands establish a base config; config list is then merged with version/tag conditionals such as `[-v6.19]`, `[-baseline]`, and `[-onlyusb]`.

State and persistence: contributes ARM-specific `.config` and command line.

Dependencies and integration points: ARM vexpress qemu platform, kernel version symbol history, syzbot parser expectations for oops stack traces, and known issue #3249 around `smp_processor_id`.

Risks: KASAN inline and unwinder choices are fragile on ARM32. Disabling branch hardening avoids a known fuzzing blocker but reduces mitigation coverage. ARM_LPAE selection intentionally excludes non-LPAE coverage.

Test signals: ARM kernels should build, boot under qemu, produce parseable oopses, and avoid the known preemptible `smp_processor_id` blocker.
