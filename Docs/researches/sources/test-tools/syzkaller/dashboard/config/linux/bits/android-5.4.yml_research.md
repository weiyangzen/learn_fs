# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.4.yml

Purpose: Android 12 5.4 LTS kernel source and defconfig selector.

Important keys: Android common repo, tag `9d0640602d7e666873e78b3d1877b8eadf529027`, and `make gki_defconfig`.

Control flow: declarative selection of checkout and initial config before shared fragments are merged.

State and persistence: contributes repo/tag/defconfig to generated kernel configs.

Dependencies and integration points: Android common 5.4 branch, GKI defconfig, config generator, and `generate.sh` for Android 5.4 config generation.

Risks: old branch compatibility with current config fragments and toolchains is the primary risk. No local overrides are present in this fragment.

Test signals: successful generated config, build, and boot on Android 5.4 syzbot setup.
