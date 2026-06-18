# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-subsystems.yml

Purpose: enables Android-specific subsystems on full, non-basefile Android kernels that are absent from `gki_defconfig` but important for fuzzing Android behavior.

Important keys: config list enables `INCREMENTAL_FS`, USB configfs/gadget functions, Android accessory/audio aliases split across pre/post 6.12 symbol names, Binder IPC selection, optional Rust Binder, and `ANDROID_BINDER_DEVICES`.

Control flow: declarative config fragment with version and feature tags such as `[-v6.12]`, `[v6.12]`, `[android-6.12]`, and `[rust]`.

State and persistence: contributes Kconfig values and Binder device string to generated configs.

Dependencies and integration points: Android common kernel Kconfig symbol history, USB gadget/configfs, Binder, syzkaller config tags, and Android full-kernel manager configs.

Risks: symbol rename handling must stay synchronized with Android branches. Disabling classic Binder IPC for `android-6.12` while enabling Rust Binder under `rust` requires tag combinations to be correct; wrong tags can leave Binder unavailable.

Test signals: generated Android full configs should expose USB gadget functions and Binder devices and boot on target managers.
