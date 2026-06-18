<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/pseudo.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/powerpc/pseudo.go

## Purpose

`pseudo.go` adds privileged pseudo-instructions to the PowerPC ifuzz backend. These are not single ISA encodings; they synthesize short instruction streams that exercise hypercalls, syscalls, ultracalls, RTAS calls, and `rfid` return-from-interrupt behavior. The file complements `powerpc.go` by using the registered instruction map and deterministic field encoders to build realistic multi-instruction byte sequences.

## Important APIs, Types, and Functions

Constants define hypercall and special-purpose-register values: `MaxHcall`, `SprnSrr0`, and `SprnSrr1`. `InsnSet.initPseudo` appends `PSEUDO_hypercall`, `PSEUDO_syscall`, `PSEUDO_ultracall`, `PSEUDO_rtas`, and `PSEUDO_rfid` as privileged pseudo instructions. The local `generator` type carries the instruction map, ifuzz config, random source, and accumulated text. Helper methods are `makeGen`, `byte`, `sc`, `rtas`, and `rfid`.

## Control Flow

`Register` in `powerpc.go` calls `initPseudo` after building the instruction map. Each pseudo instruction stores a closure that constructs a `generator`, emits a sequence, and returns `gen.text`. `sc` chooses a hypercall range, loads the call number into GPR3, loads randomized arguments into later GPRs, and emits the `sc` instruction with the requested level. `rtas` writes a token and randomized words to generated memory through `ldgpr32`, loads the custom `H_RTAS` hypercall number and argument address, then emits a level-1 system call. `rfid` loads randomized SRR0 and SRR1 values, writes them with `mtspr`, and finally emits `rfid`.

## State and Persistence Behavior

Pseudo generation is transient. Each call creates a fresh `generator` with a mutable `text` byte slice. It reads from `iset.Config` for memory-region-aware integer generation and from `rand.Rand` for register, token, hypercall, and argument selection. Persistent registration state is the appended pseudo `Insn` records in `InsnSet.Insns`; their `Priv` and `Pseudo` flags affect instruction selection and metadata but no data is written to disk.

## Dependencies and Integration Points

The file depends on `math/rand` and `github.com/google/syzkaller/pkg/ifuzz/iset`. It relies heavily on helper methods from `powerpc.go`: `ld64`, `ld32`, `ldgpr32`, `sc`, and deterministic `Insn.enc`. It also assumes generated instruction names `mtspr`, `rfid`, and the load/store/arithmetic mnemonics used by the helpers are present in `insnSetMap`. The resulting pseudo instructions integrate with the shared ifuzz mode/type indexing through `modeInsns.Add` after `initPseudo` returns.

## Risks and Edge Cases

The map lookups are unchecked, so missing generated mnemonics cause panics during pseudo generation. `rtas` derives `reg+1` without bounding against the 31-register limit, so high random registers can address an invalid paired register number in the generated field value. Hypercall range selection intentionally includes sparse ranges and may generate call numbers that are architecturally valid but unsupported by a given target. `rfid` writes arbitrary SRR0/SRR1 values, which is useful for fuzzing but can quickly leave normal control flow. All pseudo instructions are privileged and should be filtered when a non-privileged mode is desired.

## Test Signals

Tests should confirm `initPseudo` appends exactly the expected pseudo names, marks them `Priv` and `Pseudo`, and produces non-empty byte streams. Focused tests can seed `rand.Rand` to make `sc`, `rtas`, and `rfid` deterministic enough to decode the emitted instructions. Integration signals include successful generation when all required base mnemonics are present and graceful detection in tests when a reduced instruction map omits one of those dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/powerpc/pseudo.go -->
