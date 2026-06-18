# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda.h

## Purpose
Public SD/MMC/SDIO common framework header for host adapter drivers and SD-card clients.

## Main Interfaces
- SD command indexes `sda_index_t`, including normal commands and application commands.
- Response classes `sda_rtype_t`, including busy variants.
- R1/R5/R7/OCR status and capability bit macros.
- `sda_cmd_t`: command descriptor with index, response type, flags, argument, response words, block counts/sizes, residual, DMA handle/cookie, and kernel address.
- Command flags for read, write, auto CMD12, and private framework state.
- `sda_prop_t`: host/card properties for insertion, write protect, LED, clock, bus width, OCR, capabilities, and high speed.
- `sda_fault_t` and `sda_err_t`.
- `sda_ops_t`: host controller operations for command, get/set property, poll, reset, halt.
- Host lifecycle functions: init/fini ops, alloc/free, attach/detach, suspend/resume, detect, fault, transfer, log.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/note.h`. Implemented by the SD-card framework and used by host controller drivers.

## Research Notes
The header warns that consumers must not depend on `sizeof (struct sda_cmd)`.

## Notable Risks
- Command completion and transfer callbacks must respect private command flags.
- OCR and response bit handling controls card initialization and capability selection.
- Host and client APIs are distinct and should not be mixed outside the framework.
