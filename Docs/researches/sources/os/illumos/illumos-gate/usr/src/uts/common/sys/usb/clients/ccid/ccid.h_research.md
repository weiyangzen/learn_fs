# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ccid/ccid.h

## Purpose
USB CCID smart-card class protocol constants, descriptor layout, parameter structures, interrupt messages, command/response codes, and status/error definitions.

## Main Interfaces
- Defines class voltage, mechanical feature, class feature, and PIN support enums.
- Defines `ccid_class_descr_t`, matching the CCID class descriptor.
- Defines CCID version helpers and descriptor type/length constants.
- Defines protocol parameter structures `ccid_params_t0_t`, `ccid_params_t1_t`, and union `ccid_params_t`.
- Defines sequence range constants `CCID_SEQ_MIN` and `CCID_SEQ_MAX`.
- Defines interrupt slot and hardware error structures plus interrupt code enums.
- Defines request codes for host-to-reader messages and response codes for reader-to-host messages.
- Defines `ccid_header_t` and `ccid_data_clock_t`.
- Defines reply ICC/status extraction macros and enums for ICC status, command status, and command errors.
- Defines `CCID_APDU_LEN_MAX`.

## Dependencies And Relationships
Includes `sys/stdint.h`. Used by the kernel CCID driver and user ioctl layer to build and parse USB CCID messages.

## Research Notes
The structures mirror USB CCID wire formats and use fixed-width integer types. Command status and ICC status are packed into response bytes, so helper macros should be used for decoding.
