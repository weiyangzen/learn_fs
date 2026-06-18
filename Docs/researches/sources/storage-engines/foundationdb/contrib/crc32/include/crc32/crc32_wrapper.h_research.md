# sources/storage-engines/foundationdb/contrib/crc32/include/crc32/crc32_wrapper.h

## Purpose
Declares the PowerPC-specific C wrapper symbol for VPMSUM CRC.

## Important APIs, Types, And Functions
Under `__powerpc64__`, declares `extern "C" unsigned int crc32_vpmsum(unsigned int crc, unsigned char* p, unsigned long len);`. Uses include guard `FLOW_CRC32_WRAPPER_H` and `#pragma once`.

## Control Flow
Header-only declarations; no executable flow.

## State And Persistence
No state.

## Dependencies And Integration
Included by `crc32c.cpp` in the PowerPC path. Declaration must match `crc32_wrapper.c`.

## Risks
No declaration exists on non-PowerPC, so accidental non-PowerPC uses fail at compile time. The buffer pointer is not const, matching the C wrapper but less precise than the public CRC32C API.

## Test Signals
Compile a PowerPC target including this header from C++ and link against the `crc32` static library.
