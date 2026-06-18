# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.1.yml

Purpose: Android 14 6.1 kernel source and defconfig selector.

Important keys: Android common repo, tag `80ac9236949e7`, and `make gki_defconfig`.

Control flow: consumed by the config generator as checkout metadata and base defconfig command.

State and persistence: declarative only.

Dependencies and integration points: Android common 6.1 branch/tag, GKI defconfig, shared Android/base fragments.

Risks: no branch-specific overrides; shared fragments must handle symbol availability and Android branch quirks.

Test signals: generated config should build and boot for Android 6.1 fuzzing.
