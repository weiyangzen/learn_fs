# sources/test-tools/unionmount-testsuite/context.py

Purpose: core state model and operation library for unionmount/overlayfs tests. It mirrors expected filesystem state as a dentry/inode tree, runs real VFS operations, and validates copy-up, layer, device, inode, content, and error behavior.

Important APIs/types/functions: `upper` enum, `inode`, `dentry`, and `test_context`. Public operation methods include `open_file`, `open_dir`, `chmod`, `link`, `mkdir`, `readlink`, `rename`, `rmdir`, `truncate`, `unlink`, `utimes`, `rmtree`, `check_layer`, path/name helpers, layer tracking, and device/inode checks.

Control flow: setup code records lower-layer fixtures into the shadow tree. Each test operation walks paths with symlink and terminal-slash semantics, derives expected errors, prints a reproducible `./run` command, checks current layer state, performs the OS call, updates the shadow dentry state on success or failed create, validates content/size when requested, and checks layer state again. Rename/link paths update hardlink/copy-up expectations and optionally remount/rotate upper layers for recycle tests.

State and persistence: shadow state tracks dentries, inodes, layers, upper/data/meta status, lower/upper device IDs, current layer count, generated file number, cwd, and test flags. Real operations mutate the mounted test filesystem.

Dependencies and integration: imports `tool_box`, `remount_union`, `os`, `errno`, stat helpers, and test configuration. `run` creates one context per test script and subtests call its methods.

Risks: direct mode bypasses shadow path semantics; pathwalk emulates kernel behavior and may diverge on edge cases; copy-up block checks are disabled; `errorf` calls global `error` instead of `self.error`; terminal slash overrides are complex.

Test signals: every unionmount test script exercises this file. Failures produce `TestError` diagnostics and a reproducible command line.
