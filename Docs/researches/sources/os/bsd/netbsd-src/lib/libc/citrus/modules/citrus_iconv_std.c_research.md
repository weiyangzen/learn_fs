# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_iconv_std.c

Read completely: 585 lines.

This module implements the standard Citrus iconv engine. It opens source and destination ESDB records, opens their standard encodings, builds lists of usable charset mappers between source and destination charsets, then converts input by decoding to csid/index, mapping, and encoding to output.

Key functions: `open_csmapper` restricts composed mappers to stateless 1:1 mappings; `open_dsts` and `open_srcs` build sorted mapper lists by normalization cost; `do_conv` tries destination mappers and reports non-identical/no-corresponding cases; shared/context init allocate encodings and per-context state storage; `convert` handles reset calls, saves/restores encoding state around errors, tracks invalid counts, and optionally emits destination invalid replacement characters.

Important interactions: depends on ESDB, stdenc, mapper/csmapper, memstream, and Citrus iconv ABI. It is the bridge tying most files in this group into actual iconv behavior.

Security/reliability notes: state save/restore is a strong error-recovery pattern. Mapper initialization rejects stateful or non-1:1 mappers. Context allocation computes `(src_state + dst_state) * 2 + context`; if new encodings ever expose very large state sizes, overflow hardening would be prudent. The `err_norestore` label is present but unused.
