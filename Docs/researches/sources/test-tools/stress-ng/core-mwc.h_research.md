# sources/test-tools/stress-ng/core-mwc.h

Purpose: public random-number interface and inline fast bounded reduction helpers.

Important APIs/types: seed and MWC output declarations, random buffer/string helpers, and inline `stress_mwc8modn`, `stress_mwc16modn`, `stress_mwc32modn`, `stress_mwc64modn`, and `stress_mwcsizemodn`.

Control flow: with `HAVE_FAST_MODULO_REDUCTION`, bounded helpers use multiply-high reduction; 64-bit reduction additionally requires `HAVE_INT128_T`. Otherwise declarations bind to fallback implementations.

State/persistence: no header state, but all APIs operate on `core-mwc.c`'s process-global generator state.

Dependencies/integration: included widely by stressors and core helpers; depends on `stdint.h`, `core-attribute.h`, `SIZE_MAX`, and build feature macros.

Risks: comments say inclusive range but fast reduction returns `[0,max)`. Fast inline functions have no explicit `max==0` guard.

Test signals: compile int128/non-int128 paths, assert bounded range for several max values, and check 32-bit versus 64-bit `size_t` selection.
