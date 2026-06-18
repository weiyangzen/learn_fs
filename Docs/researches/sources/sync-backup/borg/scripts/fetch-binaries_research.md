# sources/sync-backup/borg/scripts/fetch-binaries

Purpose: Fetches built Borg binaries from Vagrant machines into local `dist/` artifacts for Linux glibc and FreeBSD targets.

Important APIs/types/functions: Defines Bash function `check_and_copy VM_NAME OUTPUT_BASENAME`. It uses `vagrant ssh` to run `/vagrant/borg/borg.exe -V` and `/vagrant/borg/borg-dir/borg.exe -V`, then `vagrant scp` to copy `/vagrant/borg/borg.exe` and `/vagrant/borg/borg.tgz`.

Control flow: Creates `dist/`, calls `check_and_copy` for `bullseye`, `bookworm`, `trixie`, and `freebsd14`, producing named binary and tarball outputs.

State and persistence: Writes files such as `dist/borg-linux-glibc231-x86_64`, `dist/borg-linux-glibc231-x86_64.tgz`, and analogous outputs for other targets.

Dependencies and integration points: Requires Vagrant VMs with expected names, SSH/scp support, built artifacts at fixed `/vagrant/borg/` paths, and executable Borg binaries. Integrates with binary release packaging.

Risks: No `set -e`, so failures may not abort the full script consistently. Fixed VM names and paths make it brittle. Output overwrites are silent.

Test signals: Run after building Vagrant targets, verify version commands printed for each EXE/DIR pair, check all expected `dist/` files exist, and run `glibc_check.py` for Linux binaries.
