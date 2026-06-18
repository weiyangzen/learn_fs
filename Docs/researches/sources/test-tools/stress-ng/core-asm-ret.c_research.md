# sources/test-tools/stress-ng/core-asm-ret.c

Purpose: provides architecture-specific raw return-instruction opcode bytes for generated executable-code stressors.

Important APIs and control flow: initializes global `stress_ret_opcode` with stride, length, assembler mnemonic, and up to 8 opcode bytes based on architecture and endian macros; `stress_asm_ret_supported` returns success when bytes are available or logs unsupported architecture.

State and persistence: immutable global constant; no runtime mutation.

Dependencies and integration: depends on `core-arch.h` and `core-asm-ret.h`; consumed by stressors that synthesize callable return stubs.

Risks and test signals: wrong opcodes or endian variants can crash generated code; unsupported architectures return length zero. Signals are architecture-specific generated-call tests and graceful unsupported messages.
