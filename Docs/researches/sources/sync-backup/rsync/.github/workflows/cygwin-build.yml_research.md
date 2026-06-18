# sources/sync-backup/rsync/.github/workflows/cygwin-build.yml

Purpose: CI for rsync on Cygwin.

Important APIs/types/functions: Windows runner installs Cygwin packages, configures/builds rsync, runs tests, exercises TCP daemon path where supported, and uploads Windows/Cygwin artifacts such as `rsync.exe`.

Control flow: path-filtered push/PR plus schedule. The workflow bridges GitHub Actions Windows execution with Cygwin shell/toolchain commands.

State and persistence: binary/manpage artifacts retained for inspection.

Dependencies/integration: depends on Cygwin package availability, Windows runner behavior, and rsync portability layers.

Risks: Cygwin service/network behavior can differ from Unix; package mirror issues may cause unrelated failures.

Test signals: build, version, test suite, and artifact upload validate Windows-POSIX compatibility.
