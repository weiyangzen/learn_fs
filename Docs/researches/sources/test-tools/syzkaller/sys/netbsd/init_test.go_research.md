# sources/test-tools/syzkaller/sys/netbsd/init_test.go

Purpose: regression test for NetBSD target neutralization.

Important APIs/types/functions: `TestNetBSDNeutralize` uses `prog.TestDeserializeHelper` with `targets.NetBSD` and `targets.AMD64`.

Control flow: the test deserializes a NetBSD program containing `compat_50_mknod`, lets the target initialization/neutralization path transform it, and checks the expected rewritten mode value.

State and persistence: test-only; creates no files or durable state.

Dependencies and integration points: imports `_ "github.com/google/syzkaller/sys"` so generated target registration runs, then exercises the public deserialize helper.

Risks: coverage is narrow and only proves the generic Unix neutralizer is wired for one mknod compatibility case.

Test signals: this file is itself the signal; failure indicates target registration or Unix neutralizer behavior changed.
