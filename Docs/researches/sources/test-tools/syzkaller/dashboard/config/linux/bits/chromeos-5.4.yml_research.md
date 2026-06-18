# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.4.yml

Purpose: ChromeOS 5.4 kernel source selector with a branch-specific DRM workaround.

Important keys: ChromiumOS kernel repo, tag `659b005fb0dcc1747094201a14945a6af734be50`, prepareconfig for `chromiumos-x86_64`, `make olddefconfig`, and `DRM_I915: n`.

Control flow: generator prepares the 5.4 ChromeOS config and disables `DRM_I915` to avoid a documented build error.

State and persistence: affects generated config only.

Dependencies and integration points: ChromeOS 5.4 tree, prepareconfig script, shared fragments, and DRM Kconfig/build behavior.

Risks: disabling i915 removes important GPU coverage but avoids build failure. The workaround should be revisited if the branch/compiler changes.

Test signals: build should avoid the documented `i915_selftest.h` statement-with-no-effect error.
