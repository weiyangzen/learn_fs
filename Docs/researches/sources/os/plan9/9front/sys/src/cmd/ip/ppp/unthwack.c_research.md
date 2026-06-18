# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/unthwack.c

This is the Thwack decoder. It reconstructs compressed blocks using the current output buffer plus prior decoder-history blocks identified by sequence metadata.

`unthwackinit` clears decoder state and points every `UnthwBlock` at its fixed backing buffer. `unthwackstate` returns the newest received sequence plus a mask of nearby history blocks, which the PPP glue sends back as compressor acknowledgments.

`unthwackinsert` stores a decoded or uncompressed-add block in sequence order, replacing the oldest slot. `unthwackadd` inserts a raw block into decoder history.

`unthwack` parses the compressed stream. It first reconstructs the history block list from sequence-delta and mask bytes. It then decodes literals and length/offset references using tables that mirror the encoder’s variable-length format. Output is written to a temporary decoder slot, copied to the caller’s destination, and inserted into decoder history if successful.

Errors are reported through `ut->err` and negative returns, covering missing history blocks, invalid offsets, excessive output, bad lengths, and compressed data overrun.
