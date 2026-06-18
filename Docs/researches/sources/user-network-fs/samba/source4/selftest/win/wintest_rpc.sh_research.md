# Research: sources/user-network-fs/samba/source4/selftest/win/wintest_rpc.sh

Purpose: runs selected RPC smbtorture suites against a Windows server over local RPC, named pipes, and TCP RPC transports.

Control flow: it validates arguments, defines known-working tests per transport, loops over bind options `seal,padcheck` and `bigendian`, dispatches by transport, and invokes smbtorture with credentials and domain. Failures increment `all_errs` and restore the configured VM snapshot.

State and dependencies: it does not create shares, but RPC tests may change remote server state depending on the smbtorture suite. It depends on the Windows config, smbtorture, and snapshot helper.

Risks and test signals: comments document omitted failing tests, making this a curated interoperability subset. Snapshot restore after any RPC failure is conservative but can be costly and may obscure which subtest dirtied the VM.
