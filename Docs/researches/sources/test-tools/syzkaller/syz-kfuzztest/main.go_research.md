## sources/test-tools/syzkaller/syz-kfuzztest/main.go

`syz-kfuzztest` is a Linux-only CLI wrapper for the KFuzzTest manager. It accepts flags for `vmlinux`, cooldown, thread count, and display interval, plus optional enabled target names. It builds `kfuzztest-manager.Config`, installs interrupt handling, constructs a manager, and runs it.

State is managed by the KFuzzTest manager; this file only owns process-level context cancellation. Dependencies are `pkg/kfuzztest-manager`, `osutil.HandleInterrupts`, and standard flag parsing. Risks include panic on manager creation error instead of formatted fatal logging and Linux-only build constraints limiting availability. There are no direct tests here.
