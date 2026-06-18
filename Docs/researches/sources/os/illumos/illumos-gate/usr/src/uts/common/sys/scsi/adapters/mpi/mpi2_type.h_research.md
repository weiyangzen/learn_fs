# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_type.h

## Purpose
Provides the basic scalar and pointer typedefs used by MPI v2 headers when the older `mpi_type.h` definitions have not already been included.

## Main Interfaces
- `MPI2_POINTER`: defaults to `*`, but can be overridden before inclusion for environments that need a different pointer qualifier.
- Integer typedefs:
  - `S8`, `U8`, `S16`, `U16`
  - `S32`, `U32`, with a FreeBSD-specific `int32_t`/`uint32_t` branch and a Unix/ARM/Alpha/PPC branch using `int`/`unsigned int`.
  - `S64`, `U64` as structs containing low/high 32-bit words, not native 64-bit integer typedefs.
- Pointer typedefs:
  - `PS8`, `PU8`, `PS16`, `PU16`, `PS32`, `PU32`, `PS64`, `PU64`.

## Dependencies And Relationships
This is the base type substrate for all `mpi2_*` ABI headers in this group. The `#ifndef MPI_TYPE_H` guard avoids redefining basic types if the MPI v1 type header is already present.

## Research Notes
The version is `02.00.01`. The `S64`/`U64` struct representation is significant for ABI layout: it encodes 64-bit quantities as two 32-bit words and should not be silently replaced with a compiler-native `uint64_t` in packed firmware message definitions.
