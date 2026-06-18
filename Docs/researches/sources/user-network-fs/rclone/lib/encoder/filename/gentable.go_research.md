# sources/user-network-fs/rclone/lib/encoder/filename/gentable.go

Source read signal: reviewed complete local file (129 lines, sha256 6dd62e7c87b4c97e).

Purpose: Build-tagged table generator for Huffman filename compression tables from byte histograms or indexed filename corpora.

Important APIs/types/functions: Command flags include `-index`, `-all`, and `-scsu`. `main` builds a byte histogram, optionally SCSU-encodes input lines, scales frequencies, asks `huff0` to build a table, and prints a base64 table plus sample compression statistics.

Control flow: With `-index`, it reads the file, optionally filters lines that SCSU compresses, counts bytes, and replaces the built-in example histogram. It then scales counts to about 100 KiB, fills a training slice, compresses once with `ReusePolicyNone` to obtain `OutTable`, then recompresses a sample with `ReusePolicyPrefer` for stats.

State and persistence behavior: It only reads optional input and writes generated data to stdout; maintainers manually paste table strings into `init.go`.

Dependencies and integration points: Uses `flag`, `os`, `bufio`, `unicode/utf8`, `scsu`, `huff0`, and `compress.ShannonEntropyBits`. It feeds the runtime filename table data.

Risks and test signals: Because generated tables become compatibility data, corpus choice and `-all` behavior affect future compression/decompression. Division by zero would occur if an indexed corpus produces zero total bytes; generated tables need decode tests before use.
