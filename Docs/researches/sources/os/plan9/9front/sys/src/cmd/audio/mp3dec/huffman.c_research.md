# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.c

This file is static Layer III Huffman lookup data derived from ISO/IEC 11172-3 Table B.7. It defines quad tables `hufftabA` and `hufftabB` for count1 regions and pair tables `hufftab0`, `hufftab1`, `hufftab2`, `hufftab3`, `hufftab5`, `hufftab6`, `hufftab7`, `hufftab8`, `hufftab9`, `hufftab10`, `hufftab11`, `hufftab12`, `hufftab13`, `hufftab15`, `hufftab16`, and `hufftab24`.

The table entries use local `PTR` and `V` macros to represent either intermediate lookup nodes or final decoded symbols with Huffman length metadata. The layout supports decoding up to four Huffman bits at a time, with occasional secondary lookups through offsets. At the end, `mad_huff_quad_table[2]` exposes the two quad tables, and `mad_huff_pair_table[32]` maps MPEG table-select indices to table pointers, `linbits`, and starting lookup widths. Unused table-select values are represented with null entries.

There is no executable decode routine here; `layer3.c` consumes these tables in `III_huffdecode`. The correctness and shape of this data directly determine Layer III spectral coefficient decoding.
