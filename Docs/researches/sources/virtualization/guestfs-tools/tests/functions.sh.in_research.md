# File Research: sources/virtualization/guestfs-tools/tests/functions.sh.in

Autoconf-substituted shared shell helper library for guestfs-tools tests.

Key behavior:
- Clears `CDPATH` and sets `LANG=C`.
- Defines top source/build paths, absolute source/build paths, current test build/source dirs, and sources generated `config.sh`.
- Provides skip helpers:
  - `skip_if_skipped` from `SKIP_<script>` env vars,
  - backend include/exclude checks,
  - phony guest existence,
  - architecture include/exclude checks,
  - virt-builder guest availability,
  - FUSE availability,
  - daemon feature availability,
  - filesystem availability,
  - libvirt minimum version,
  - environment variable presence,
  - command availability,
  - explicit broken-test skip,
  - root/non-root test gating,
  - slow-test gating.
- Provides checksum helpers for MD5, SHA1, and SHA256 on Linux.

Research notes:
- Exit status 77 is consistently used for skipped tests.
- Most shell tests in this group source this file immediately, then enable `set -e` and `set -x`.
