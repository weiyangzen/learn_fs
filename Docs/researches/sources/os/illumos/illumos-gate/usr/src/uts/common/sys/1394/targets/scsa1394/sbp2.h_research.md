# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/targets/scsa1394/sbp2.h

## Purpose

`sbp2.h` defines SCSI command and status encapsulation structures for SBP-2 transport.

## Main Types

`scsa1394_cmd_orb_t` is the SBP-2 command ORB format. It includes the next ORB pointer, two-word data descriptor, parameter field, data size, and a 12-byte SCSI CDB.

`scsa1394_status_t` is the SBP-2 status block with SBP status, ORB offset, SCSI status, sense bits, sense code/qualifier, information bytes, CDB-dependent data, FRU, sense-key-specific bytes, and vendor-dependent fields.

## Constants

The header defines masks and shifts for SCSI status format and status code, status block formats, sense valid/filemark/EOM/ILI/sense-key bits, and FRU/sense-key-dependent fields.

## Research Notes

This is the wire-format bridge between SBP-2 status transport and illumos SCSI sense/status handling. It is small but central to command completion correctness.
