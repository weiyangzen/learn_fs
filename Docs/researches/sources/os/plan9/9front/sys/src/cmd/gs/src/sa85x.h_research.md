# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85x.h

Declares the ASCII85Encode filter state and stream template. It includes `sa85d.h` and defines encoder state fields for output line digit count and last character written.

The inline initialization sets line count to zero and last character to newline. The actual encoder implementation is elsewhere, while this header supplies the shared state layout and `s_A85E_template`.

Dependencies are Ghostscript stream common definitions and ASCII85Decode declarations.
