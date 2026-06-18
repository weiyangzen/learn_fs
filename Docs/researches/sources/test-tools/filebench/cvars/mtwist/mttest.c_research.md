<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mttest.c -->
# `sources/test-tools/filebench/cvars/mtwist/mttest.c`

Purpose: C test and benchmark harness for the C Mersenne Twister API.

Important APIs/functions: `main`, `report_timing`, `report_clock_timing`, and exercised APIs `mt_seed32new`, `mt_savestate`, `mt_loadstate`, `mt_lrand`, `mts_lrand`, `mt_llrand`, `mts_llrand`, `mt_drand`, `mts_drand`, `mt_ldrand`, `mts_ldrand`, `mt_seed`, `mt_goodseed`, and `mt_bestseed`.

Control flow: optional argument sets timing loop count in millions. It seeds with `5489`, saves default state to `mtsave`, changes seed, restores state, unlinks the file, compares generated values against a reference vector, verifies function pointers, runs default and explicit-state timing loops for integer and double generation, then times seed functions.

State and persistence: uses global default MT state and a static local `mt_state`. Creates temporary file `mtsave` for save/load validation. Timing accumulators are assigned to volatile variables to prevent optimization.

Dependencies and integration: includes `mtwist.h`, `inttypes.h`, `unistd.h`, `stdio.h`, `stdlib.h`, `sys/resource.h`, and `sys/time.h`. Validates the C interface implemented by `mtwist.c`.

Risks: fixed temp filename is not parallel-safe. Default 300 million loops are costly. Static `mt_state state` is zero-initialized and intentionally relies on lazy seeding. Seed timing can block or vary if `/dev/random` is slow.

Test signals: validity pass/fail, nonzero exit on reference mismatch, timing reports, and warnings if `mt_seed`/`mt_goodseed` return zero or the same seed.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/cvars/mtwist/mttest.c -->
