# sources/test-tools/ltp/testcases/kernel/fs/doio/datapid.c

Purpose: Cray-specific data pattern generator/checker that embeds pid and file offset into machine words for doio validation.

Important APIs/types/functions: `datapidgen`, `datapidchk`, macros `LOWER16BITS`, `LOWER32BITS`, `NBPBYTE`, conditional `CRAY`, static `Errmsg`, and optional K&R-style `UNIT_TEST` main.

Control flow: under `CRAY`, generation handles partial leading word, full words, and partial trailing word. Each word encodes lower 16 bits of pid, lower 32 bits of the word's file offset, and lower 16 bits of pid. Checking reconstructs the same expected words and returns the absolute offset of the first mismatching byte, or `-1` on success. On non-CRAY builds, generation returns `-1`; checking sets the error message to "Not supported on this OS." and returns `0`.

State/persistence behavior: writes caller buffers and uses static error text. It has no external state.

Dependencies/integration: retained for legacy doio portability; behavior is meaningful only when compiled with CRAY word-size assumptions and `NBPW` available.

Risks/test signals: on normal Linux builds `datapidchk` returns `0`, which conventionally means mismatch at offset zero rather than unsupported success, so callers must understand this mode. The code uses assignment in conditionals intentionally but can trip modern warnings.
