## sources/test-tools/fio/crc/crc64.h

Purpose: declaration header for fio CRC64 routines.

Important APIs: declares `fio_crc64(const unsigned char *, unsigned long)` and incremental `fio_crc64_nvme(unsigned long long crc, const void *p, unsigned int len)`.

State and persistence: no state.

Dependencies and integration: consumed by CRC users and implemented in `crc64.c`.

Risks and test signals: both functions return `unsigned long long`, so callers need consistent width assumptions. Compile and known-answer CRC64 tests validate the contract.
