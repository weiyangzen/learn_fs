# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.12.yml

Purpose: Android 16 6.12 kernel source selector with a Rust Binder boot-argument tweak.

Important keys: Android common repo, tag `5150a2974c100f8aa5cbfa9a09d804ee4369f61e`, `make gki_defconfig`, and `CMDLINE: [append, "binder.impl=rust"]`.

Control flow: generator checks out/tag configures GKI, then appends Binder implementation selection to the kernel command line.

State and persistence: declarative; affects generated config and boot command line.

Dependencies and integration points: Android 6.12 common kernel, GKI defconfig, Android subsystem fragment where Rust Binder can be enabled with tags.

Risks: forcing `binder.impl=rust` depends on kernel support and matching `ANDROID_BINDER_IPC_RUST` config. If the branch changes default Binder implementations, this can alter fuzzing coverage or boot behavior.

Test signals: build/boot should confirm Rust Binder availability and stable boot with the appended command line.
