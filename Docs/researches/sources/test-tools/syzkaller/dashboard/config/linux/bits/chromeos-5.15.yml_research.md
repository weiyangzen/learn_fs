# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.15.yml

Purpose: ChromeOS 5.15 kernel source and prepareconfig selector.

Important keys: ChromiumOS kernel repo, tag `e931c5c3244d7ebba8856dc6aed54a5d1a85975e`, prepareconfig for `chromiumos-x86_64-generic`, and `make olddefconfig`.

Control flow: declarative checkout and shell setup before shared fragments.

State and persistence: contributes generated config base.

Dependencies and integration points: ChromeOS 5.15 kernel tree, prepareconfig tooling, shared ChromeOS subsystem/common fragments.

Risks: no local overrides; any ChromeOS 5.15-specific build break must be handled elsewhere.

Test signals: generated config builds and boots on ChromeOS 5.15 managers.
