# sources/test-tools/syzkaller/sys/openbsd/init_test.go

Purpose: OpenBSD neutralization regression suite.

Important APIs/types/functions: `TestNeutralize` feeds many `prog.DeserializeTest` cases into `prog.TestDeserializeHelper` for `targets.OpenBSD/targets.AMD64`.

Control flow: each case deserializes a textual syzkaller program and checks either exact rewritten output or no-change behavior. The cases target known VM-safety rewrites.

State and persistence: test-only, no durable state.

Dependencies and integration points: depends on generated sys registration via blank import and verifies OpenBSD `InitTarget` is used by the generic program deserialize path.

Risks: tests encode numeric constants, so upstream OpenBSD constant changes can require fixture updates. They do not directly test `AnnotateCall`.

Test signals: broad positive signal for the OpenBSD safety policy around flags, ioctls, device numbers, rlimits, sysctls, and wall-clock updates.
