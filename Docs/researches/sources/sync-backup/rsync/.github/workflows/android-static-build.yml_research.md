# sources/sync-backup/rsync/.github/workflows/android-static-build.yml

Purpose: cross-compile static Android rsync binaries.

Important APIs/types/functions: matrix builds `arm64-v8a` and `armeabi-v7a` using Android NDK clang, API level 24, static linking, bundled popt/zlib, disabled optional libraries/features, and qemu smoke execution.

Control flow: installs autoconf/automake/gawk/qemu, sets cross tools, exports configure cache values for Android cross-probing, builds `proto.h` serially to avoid header races, builds and strips `rsync`, checks file output for static linkage, runs `--version` under qemu, packages SHA256, and uploads artifacts.

State and persistence: artifact per ABI retained 45 days.

Dependencies/integration: integrates with GitHub-hosted NDK variables and qemu-user-static.

Risks: qemu test is best-effort; no full test suite runs for cross builds. Forced configure cache values must track Android behavior.

Test signals: architecture/static checks, qemu `--version`, and artifact checksums.
