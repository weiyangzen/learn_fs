# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/flfmt.c

Fossil filesystem formatter and initializer.

It validates/partitions a target file or device, writes the fossil header, zeros label blocks, creates root/source/meta blocks, initializes the superblock, and then opens the new filesystem to create top-level `/active`, `/archive`, and `/snapshot` directories. It supports block-size selection, label naming, overwrite confirmation bypass, Venti-root restoration, and optional ISO9660 embedding.

When restoring from Venti, it validates the supplied root score, reads the Venti root/source entries, imports qid space from the root metadata, and builds a new local top-level source pointing at the imported content.
