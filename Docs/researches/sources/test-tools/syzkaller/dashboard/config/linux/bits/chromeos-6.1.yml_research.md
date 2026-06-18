# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.1.yml

Purpose: ChromeOS 6.1 kernel source selector with io_uring enabled.

Important keys: ChromiumOS kernel repo, tag `ebea4d55ca782539782702c2e5e86033b9f86bd2`, prepareconfig for `chromiumos-x86_64-generic`, `make olddefconfig`, and config `IO_URING`.

Control flow: checkout/prepareconfig followed by config merge enabling io_uring.

State and persistence: declarative generated-config input.

Dependencies and integration points: ChromeOS 6.1 tree, prepareconfig, and syzkaller io_uring coverage.

Risks: explicitly enabling io_uring increases coverage but can expose branch-specific io_uring bugs. If prepareconfig already sets a conflicting value, merge order matters.

Test signals: ChromeOS 6.1 configs should build/boot and expose io_uring.
