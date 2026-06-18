# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdt.h

Public-facing internal interface for `pdfwrite` text and font handling. It is intended as the only text/font subsystem header included by pdfwrite code outside `pdftext.dev`.

Key contents:
- Declares allocation and reset functions for text state and text data.
- Declares page/document lifecycle hooks: reset at page start, reset after `grestore`, close page text state, and close/write text-related document resources.
- Declares content-context transitions from stream/string context into text context and a close hook for text contents.
- Declares bitmap-font support functions used by bitmap output: character image Y offset, CharProc begin/end, and image-as-character emission.
- Notes that declarations deliberately duplicate subsystem-private headers so the compiler can check consistency.

Notable dependencies:
- References types from `gdevpdfx.h` and text/font subsystem headers without exposing their full implementations.
- Function comments point to the implementation headers/files that own each function, such as `gdevpdts.h`, `gdevpdti.h`, and `gdevpdtw.h`.

Research notes:
- This header is a narrow façade over the text subsystem, not the full internal structure definition.
- It separates general pdfwrite code from lower-level font resource, encoding, bitmap, and text-state details.
- No filesystem interfaces are present.
