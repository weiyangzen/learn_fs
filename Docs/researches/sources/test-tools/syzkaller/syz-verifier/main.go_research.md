## sources/test-tools/syzkaller/syz-verifier/main.go

This file is the entrypoint and setup path for `syz-verifier`, a tool that compares execution behavior across multiple kernel configs. `Setup` creates a `Kernel` context with reporter, rpcserver, VM pool, dispatcher, enabled-syscall channel, feature channel, and crash channel. `main` loads at least two configs unless debug mode, ensures shared workdir, creates one plain queue per kernel, and starts `Verifier.RunVerifierFuzzer`.

The setup forces `cfg.Experimental.ResetAccState = true` so executor state resets between program executions. It uses the first config's workdir/target as verifier-wide state, and each kernel gets an ID/source queue. Dependencies include mgrconfig, rpcserver, report, VM dispatcher, queue, logging, and shutdown context.

State persists mainly through workdir corpus/crash store used by verifier internals. Integration is with `verifier.go` and syzkaller VM/rpc runner protocol. Risks include requiring same workdir, mutating config experimental fields, allowing single-kernel debug mode, and fatal exits for setup errors. There are no direct tests in this file.
