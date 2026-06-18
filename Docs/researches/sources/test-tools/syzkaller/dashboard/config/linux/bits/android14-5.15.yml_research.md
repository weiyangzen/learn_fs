# sources/test-tools/syzkaller/dashboard/config/linux/bits/android14-5.15.yml

Purpose: Android 14 5.15 kernel source and defconfig selector.

Important keys: Android common repo, tag `0772c040aea2`, and `make gki_defconfig`.

Control flow: declarative checkout and defconfig metadata for the config generator.

State and persistence: no runtime state; contributes to generated configs.

Dependencies and integration points: Android 14 5.15 common kernel branch, GKI defconfig, shared Android fragments.

Risks: no local overrides, so build/boot stability depends on shared fragments and the pinned tag.

Test signals: successful Android 14 5.15 build and boot in syzbot.
