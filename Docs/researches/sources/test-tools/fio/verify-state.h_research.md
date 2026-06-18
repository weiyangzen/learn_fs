# sources/test-tools/fio/verify-state.h

Purpose: wire-format and helper declarations for fio verify-state save/load files. These files allow later verification runs to know random offset state, inflight writes, failed writes, and stop thresholds.

Important APIs/types: `thread_rand32_state`, `thread_rand64_state`, and `thread_rand_state` serialize random generator state. `inflight_write` stores `numberio`. `thread_io_list` is a variable-length per-thread record with depth, threshold `numberio`, thread index, RNG state, job name, and inflight array. `all_io_list` aggregates thread records. `verify_state_hdr` stores version, size, and CRC. Inline helpers compute record sizes, walk to the next record, and generate escaped state filenames.

Control flow/state: consumers write a header followed by one `thread_io_list`; sizes are little-endian on disk. `verify_state_gen_name()` replaces `/` with `.` and emits `<prefix>-<escaped-name>-<num>-verify.state`.

Dependencies/integration: includes endian helpers indirectly from fio headers, `PATH_MAX`, and `nowarn_snprintf`. Implemented by `verify.c`.

Risks/test signals: variable-length structs require exact size calculations and endian conversion. State-file compatibility depends on `VSTATE_HDR_VERSION`. Tests should cover filename escaping, CRC rejection, version rejection, and mixed-depth state walking.
