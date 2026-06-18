# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.15.yml

Purpose: Android 13 5.15 LTS kernel source and defconfig selector.

Important keys: `kernel.repo` points to Android common, `kernel.tag` is `241da2ad56013`, and `shell` runs `make gki_defconfig`.

Control flow: the config pipeline checks out the tag and starts from GKI defconfig before applying shared Android/base fragments.

State and persistence: declarative only; affects generated kernel source selection and `.config`.

Dependencies and integration points: Android common 5.15 branch/tag and the dashboard Linux config generator.

Risks: no branch-specific config overrides are present, so this relies entirely on shared fragments. If Android 5.15 needs special disables, build/boot failures will surface downstream.

Test signals: generated Android 5.15 config should build and boot under syzbot managers.
