# sources/test-tools/ltp/testcases/kernel/fs/doio/pattern.c

Purpose: fills buffers with a repeating byte pattern and verifies that a buffer still matches that repeated pattern at a given shift. The routines are small data-integrity helpers for doio read/write validation.

Important APIs/types/functions: `pattern_fill`, `pattern_check`, `memcmp`, `memcpy`, `patlen`, and `patshift`.

Control flow: both functions normalize `patshift` modulo `patlen`, handle the split first pattern copy/compare when the shift is nonzero, then use a doubling-style copy/compare against the already-filled prefix to cover the rest of the buffer efficiently.

State/persistence behavior: all state is caller-owned memory. `pattern_fill` modifies `buf`; `pattern_check` reads `buf` and returns `0` on match or `-1` on mismatch. No global or persistent state is used.

Dependencies/integration: included through `pattern.h` by doio data paths that need deterministic write patterns and later verification.

Risks/test signals: callers must provide a nonzero pattern length for meaningful operation; a zero pattern length would make the first transfer length equal to zero and risk a non-progressing loop. The direct signal is `0` for valid data and `-1` for corruption.
