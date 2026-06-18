# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pfmod.h

## Purpose
Defines the STREAMS packet-filter module ioctl ABI and the encoded packet-filter instruction language.

## Main Interfaces
- `PFIOCSETF`: ioctl to replace the current packet filter.
- Filter sizes:
  - `ENMAXFILTERS`
  - `PF_MAXFILTERS`
- Filter structures:
  - `struct packetfilt`
  - `struct Pf_ext_packetfilt`
- Instruction encoding:
  - action/operator bit split: `ENF_NBPA`, `ENF_NBPO`
  - operators: `ENF_EQ`, `ENF_LT`, `ENF_GE`, `ENF_AND`, `ENF_OR`, `ENF_XOR`, `ENF_NEQ`, and conditional variants.
  - actions: `ENF_PUSHLIT`, `ENF_PUSHZERO`, `ENF_LOAD_OFFSET`, `ENF_BRTR`, `ENF_BRFL`, `ENF_POP`, `ENF_PUSHWORD`.

## Dependencies And Relationships
Used by consumers that install packet filters on open Ethernet/packet streams. The filter executes as a stack machine over 16-bit words and accepts packets when the final stack value is true.

## Research Notes
The extended structure increases filter length from 255 to 2047 short words. The comments document the virtual machine semantics and ownership rules for the filter command list.
