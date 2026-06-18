# sources/test-tools/unionmount-testsuite/settings.py

Purpose: configuration object for unionmount tests, translating environment variables and CLI flags into mount roots, filesystem type/name, mount options, feature flags, and test mode.

Important APIs/types/functions: `config` methods for testing mode, base/lower/upper/union roots, mount decisions, lower image/testdir paths, verbosity/verify/maxfs/samefs/squashfs/erofs/xino/metacopy/nested/fuse flags, and mount options.

Control flow: constructor reads `UNIONMOUNT_BASEDIR`, `UNIONMOUNT_LOWERDIR`, `UNIONMOUNT_MNTPOINT`, and `UNIONMOUNT_MNTOPTIONS`, prints them, normalizes mount options to start with `-o`, derives default maxfs/samefs behavior, and initializes flags. Later setters are called by `run` as CLI parsing and feature detection proceeds.

State and persistence: configuration is in memory; constructor prints environment details to stdout. Paths point to `/base`, `/lower`, `/upper`, and `/mnt` by default unless overridden.

Dependencies and integration: used by setup, mount, remount, context, direct mode, and run driver.

Risks: environment values are passed to shell commands elsewhere without quoting; constructor prints every run; samefs inference from `UNIONMOUNT_BASEDIR` plus empty lowerdir is implicit; mount option string is mutable comma concatenation.

Test signals: coverage comes from running the suite under each mode/flag combination.
