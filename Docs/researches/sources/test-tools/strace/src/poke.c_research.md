<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/poke.c -->
# sources/test-tools/strace/src/poke.c

Purpose: stores and applies syscall tampering payloads that write bytes into tracee memory on syscall entry or exit.

Important APIs/types/functions: `alloc_poke_data`, `poke_add`, `poke_tcb`, `struct poke_payload`, `poke_data_vec`, and list helpers.

Control flow: allocation grows an arena of list heads and returns a 16-bit index. `poke_add` rejects duplicate `(is_enter,arg_no)` payloads per index. `poke_tcb` iterates payloads for the current phase, validates argument count, writes data to the pointer argument with `upoken`, logs failures, and marks `TCB_TAMPERED_POKED` if any write succeeds.

State and persistence behavior: process-wide `poke_data_vec` stores payload lists for the lifetime of strace.

Dependencies and integration points: used by fault/injection qualifier logic; depends on `list.h`, `upoken`, syscall metadata `n_args`, and tcb flags.

Risks: writes target tracee memory and can intentionally perturb behavior. Argument numbers are one-based in payloads but zero-based in `u_arg`; validation must remain correct. Index overflow is fatal.

Test signals: allocation growth, duplicate rejection, entry and exit pokes, invalid argument number, failed `upoken`, successful tamper flag, and multiple payloads per syscall.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/poke.c -->
