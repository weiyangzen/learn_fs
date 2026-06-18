# sources/security-integrity/libcap/pam_cap/sudotest.conf

Purpose: test configuration for privileged `pam_cap` scenarios, not a system default.

Important format and behavior: contains ordered rules for root and test users. `all root` preserves root IAB state. Specific rules exercise bounding drops (`!cap_chown`), inheritable additions (`cap_setuid,cap_chown`), group matching with `@three` and `@one`, invalid non-group prefix `+one`, and ambient/inheritable markers with `^`.

Control flow/integration: consumed by `pam_cap.c` when a test passes `config=./sudotest.conf` or equivalent. The first matching rule wins, so comments explicitly mark rules that should or should not fire.

State and dependencies: no runtime state; depends on the test harness' synthetic user/group map.

Risks and test signals: verifies rule ordering and group selector precedence. A change here can invalidate expected bitmasks in `test_pam_cap.c` and sudo-style integration tests.
