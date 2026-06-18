# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/pangen6.h

This file is not ordinary compiled C for Spin itself; it is a generated-code template, `static char *Code2c[]`, emitted into generated `pan` verifiers when `NCORE>1`. It contains the multi-core verifier support layer for Spin 5.x-era pan code.

The template defines shared-memory queue frames (`SM_frame`), result aggregation records (`SM_results`), and shared allocation pools (`sh_Allocater`). It supports both Unix/System V shared memory and Windows file mappings. The frame layout serializes a verifier state vector, mask bits, process and channel offsets/skips, C tracked-state stack data under `C_States`, and optional `FULL_TRAIL` stack-tree links.

Major generated subsystems:
- Multi-core configuration constants: `NCORE`, `VMAX`, `PMAX`, `QMAX`, queue sizes, crash/termination timing, and disk spill limits.
- Shared memory setup: `init_shm`, `prep_shmid_S`, `prep_state_mem`, `init_HT`, `init_SS`, and platform-specific cleanup.
- Interprocess locking: `tas`, `e_critical`, `x_critical`, `iam_alive`, and crash detection via shared `is_alive`.
- State handoff: `mem_put`, `mem_put_acc`, `mem_hand_off`, `Get_Free_Frame`, `Get_Full_Frame`, `GlobalQ_HasRoom`.
- Queue reading and termination detection: `Read_Queue` circulates `QUERY`, `QUERY_F`, and `QUIT` control frames and folds per-core stats with `record_info`/`retrieve_info`.
- Error trail support: `cur_Root`, `write_root`, `set_root`, and optional `Stack_Tree` history for `FULL_TRAIL`.
- Optional disk overflow path under `USE_DISK`: `mem_file`, `mem_drain`, and disk stats/cleanup.

Notable constraints and coupling:
- Multi-core mode explicitly rejects `BFS`, `SC`, and some `MA` combinations.
- State handoff is blocked in certain atomic/rendezvous/claim-move situations to preserve verifier semantics.
- `m_vsize` is used as the publication flag and is written last when filling a frame.
- The code assumes fixed upper bounds for serialized process/channel metadata; exceeding them requires recompilation with larger `VMAX`, `PMAX`, or `QMAX`.

Risk notes:
- This template uses manual shared memory layout and pointer arithmetic with word-alignment fixes; portability and 32/64-bit behavior depend on the generated compile environment.
- It uses busy waits and timeout heuristics for crash and termination detection.
- Some counters are intentionally read outside locks for performance, relying on benign races.
