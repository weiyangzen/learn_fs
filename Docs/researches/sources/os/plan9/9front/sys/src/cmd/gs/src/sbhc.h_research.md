# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbhc.h

Declares BoundedHuffman filter states and templates. The common state embeds Huffman state, an `hc_definition`, client-set `EndOfData` and `EncodeZeroRuns`, and a dynamic `zeros` counter.

Separate encode/decode states add `hce_table` or `hcd_table` storage and GC descriptors for allocated definition/table arrays. The header also provides inline init and decode state load/store macros.

Dependencies include `shc.h` and `strimpl.h`. This is stream compression infrastructure.
