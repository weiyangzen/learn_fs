# sources/test-tools/syzkaller/executor/kvm_ppc64le.S

Purpose: ppc64le assembly snippets converted into byte arrays for KVM setup tests.

Important APIs and control flow: `LOAD64` materializes a 64-bit immediate into a register. `kvm_ppc64_mr` loads `0xbadc0de`, moves it through registers, and leaves it in GPR3. `kvm_ppc64_ld` stores `0xbadc0de` near the end of the executor's expected VM memory and reloads it into GPR3. `kvm_ppc64_recharge_dec` reloads the decrementer SPR and returns from interrupt with `rfid`.

State and dependencies: relies on guest memory sizing/layout assumptions from KVM setup code and `kvm.h`. Symbol `_end` markers are used by `kvm_gen.cc`.

Integration points: generated into `kvm_ppc64le.S.h` and exercised by Linux ppc64le `test_kvm`.

Risks and tests: hardcoded memory offsets must match the memory region used by tests. Instruction encoding correctness is validated only through generation and KVM execution.
