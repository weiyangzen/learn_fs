## sources/test-tools/syzkaller/pkg/ifuzz/x86_test.go

Purpose: regression coverage for x86 instruction decoding at the package-ifuzz level.

Important APIs/types/functions: `regTestCase` pairs hex byte streams with `iset.Mode`. `TestDecodeRegression` decodes two hard-coded instruction streams in long-64 and protected-16 modes using `iset.Arches[ArchX86].Decode`.

Control flow: each hex string is decoded, then repeatedly sliced by returned instruction size until all bytes are consumed; zero size or error fails the test for the remaining bytes.

State and persistence: no state beyond local test buffers.

Dependencies and integration: depends on x86 package registration side effects, `encoding/hex`, and generic `iset` decode interface. Exercises real decoder registration rather than a local x86 symbol.

Risks: limited to two regressions and only checks decode progress, not semantic identity. Failures can indicate registration, decoder, or instruction table issues.

Test signals: useful smoke/regression signal for complicated privileged/pseudo sequences that previously failed decoding.
