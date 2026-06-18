# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.10.yml

Purpose: ChromeOS 5.10 kernel source and prepareconfig selector.

Important keys: ChromiumOS kernel repo, tag `ea6af77b55e49ce0cfbdd5543fe75fc8744cbd92`, and shell commands using `CHROMEOS_KERNEL_FAMILY=chromeos chromeos/scripts/prepareconfig chromiumos-x86_64-generic ${BUILDDIR}/.config` followed by `make olddefconfig`.

Control flow: generator checks out the tag and runs ChromeOS prepareconfig to seed `.config`.

State and persistence: declarative source/defconfig metadata for generated configs.

Dependencies and integration points: ChromiumOS kernel tree layout, prepareconfig script, `BUILDDIR`, and shared ChromeOS fragments.

Risks: prepareconfig command and board name are branch-specific. Pinned tag can become stale relative to ChromeOS branch fixes.

Test signals: successful ChromeOS 5.10 config generation, build, and boot.
