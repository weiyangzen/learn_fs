# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/scf.h

Common CCITTFax encode/decode definitions. It documents Group 3/Group 4 fax run-length Huffman coding, declares encoding tables, decoding tables, EOL and 2-D code constants, exceptional decode values, and run-detection macros.

The macros `skip_white_pixels` and `skip_black_pixels` are performance-sensitive scanners over packed bitmap rows. They account for `BlackIs1` polarity and use byte bit-run tables to skip long same-color runs efficiently.

Dependencies include `shc.h`, architecture sizing macros, and bit-run helper tables declared elsewhere.

This is image compression support for fax/PDF streams, not filesystem logic.
