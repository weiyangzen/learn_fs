# sources/test-tools/xfstests-bld/fstests-bld/popt/tdict.c

Purpose: sample/test program for `poptBits` Bloom-filter functionality using a dictionary file. It loads `/usr/share/dict/words`, builds a bitset, converts leftover command arguments into another bitset, intersects them, and reports membership hits/misses.

Important functions/state: `loadDict` reads words, strips whitespace/comments, and calls `poptSaveBits`. Global options expose `--debug` and toggleable `--verbose`. Globals track dictionary filename, `dictbits`, and hit/miss counters.

Control flow: main first counts dictionary lines to scale `_poptBitsN/M/K`, parses command options, reloads dictionary into `dictbits`, builds `avbits` from remaining args with `poptBitsArgs`, intersects a copy with dictionary bits, then checks each leftover word with `poptBitsChk`.

State/persistence: bitsets are heap allocations and freed at exit. Global `poptBits` sizing values are modified before bitset creation, affecting subsequent poptBits allocations in this process.

Dependencies/integration: depends on popt parser, `poptBits` API, libc file I/O, and a system dictionary path. It includes `system.h`, `stdio.h`, and `popt.h`.

Risks: Bloom filters can false-positive; this test cannot prove exact dictionary membership. Missing dictionary file makes the program fail. `poptBitsDel` semantics are not tested here.

Test signals: useful as a smoke test for `poptSaveBits`, `poptBitsArgs`, union/intersection, and toggle options; output includes bitset sizing and hit/miss totals.
