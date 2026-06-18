# File Research: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.h

## Purpose
Declares shared constants, globals, data structures, and helper prototypes for the partitioning plugin.

## Main Contents
Defines sector size, MBR size limit estimate, GPT partition table array sizing, alignment defaults, default MBR/GPT partition types, partition type enum values, `struct file`, vector type `files`, global vectors/buffers, and prototypes for virtual layout, GUID parsing, MBR entry creation, and MBR/GPT layout creation.

## Dependencies
Uses common rounding, GPT, and regions headers.

## Risks and Notes
The header exposes many mutable globals shared across the partitioning source files. `GPT_PTA_SIZE` and `GPT_PTA_LBAs` are macros dependent on `the_files.len`, so they must only be evaluated after configuration has populated the file vector.
