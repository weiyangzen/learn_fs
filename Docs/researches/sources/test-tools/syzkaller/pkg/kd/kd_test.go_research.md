## sources/test-tools/syzkaller/pkg/kd/kd_test.go

Purpose: regression test for KD exception packet decoding.

Important APIs/types/functions: build tag `!s390x`, `TestCanned`, and `exceptionPacket`.

Control flow: decodes a fixed byte packet and asserts packet starts at zero and consumed size equals packet length; logs decoded report text.

State and persistence: none.

Dependencies and integration: protects unsafe decoder behavior on supported architectures.

Risks: does not assert decoded content, only framing.

Test signals: catches struct-size/header regressions and some endian/layout issues.
