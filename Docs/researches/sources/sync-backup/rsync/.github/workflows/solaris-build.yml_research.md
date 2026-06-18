# sources/sync-backup/rsync/.github/workflows/solaris-build.yml

Purpose: Solaris portability CI.

Important APIs/types/functions: uses `vmactions/solaris-vm@v1`, installs bash/automake/m4/python/autoconf/gcc/git, configures with rrsync and disables some optional libraries/man generation, builds, runs default and TCP tests, smokes `rsync-ssl`, and uploads artifacts.

Control flow: scheduled weekly plus path-filtered push/PR. The `usesh: true` option runs shell commands inside the VM.

State and persistence: `solaris-bin` artifact retained 45 days.

Dependencies/integration: validates Solaris configure probes and portability logic.

Risks: one configure command uses `-disable-zstd`, which looks like a single-dash typo and may be ignored or treated unexpectedly depending on configure parsing.

Test signals: build, `make check`, TCP tests, ssl listing smoke, and artifact upload.
