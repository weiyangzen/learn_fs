# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.10.yml

Purpose: Android 13 5.10 LTS kernel fragment selecting the Android common repo/tag, GKI defconfig, and Android-5.10-specific mitigations.

Important keys: `kernel.repo` is `https://android.googlesource.com/kernel/common`, `kernel.tag` is `3a582928e6d19`, `shell` runs `make gki_defconfig`, and `config` disables `IO_URING` plus handles Android's `KASAN_STACK_ENABLE` to `KASAN_STACK` rename with override tags.

Control flow: declarative input to config generation. The generator checks out the given tag, runs the shell defconfig command, then applies config entries.

State and persistence: contributes selected repo/tag and final `.config`; no local state itself.

Dependencies and integration points: Android common kernel, GKI config, syzkaller config-bit parser, and version/tag labels. The io_uring comment documents a policy decision based on unbackportable 5.10 bugs.

Risks: pinning an old tag may miss security/stability updates. Disabling `IO_URING` reduces syscall coverage but avoids known noisy/unfixed crashes. KASAN rename overrides are branch-specific and may need removal when branch config changes.

Test signals: successful Android 5.10 build/boot and reduced io_uring false-positive/noise rate.
