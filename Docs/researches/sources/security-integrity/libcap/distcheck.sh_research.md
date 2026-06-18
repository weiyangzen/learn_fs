## sources/security-integrity/libcap/distcheck.sh

Purpose: release sanity script that checks whether libcap's bundled `include/uapi/linux/capability.h` names the same `CAP_LAST_CAP` as the current upstream Linux kernel header.

Important APIs/functions: shell variables `actual` and `working`; external commands `wget`, `grep`, and `awk`.

Control flow: downloads Torvalds tree's raw capability header, extracts the third field from the `#define CAP_LAST_CAP` line, extracts the same value from the local libcap header, prints success and exits 0 if equal, otherwise prints `want`/`have` and exits 1.

State/persistence: no persistent writes; network read only.

Dependencies/integration: requires network access to `git.kernel.org`, `wget`, and a source tree rooted at libcap so `libcap/include/uapi/linux/capability.h` exists. Integrates with release/distribution checks.

Risks: network instability or upstream format changes can produce false failures; it only compares the last capability macro, not comments, individual names, or semantic drift.

Test signals: mock or cache the upstream header and verify equal/unequal paths; run in CI with network optionality documented.
