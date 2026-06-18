## sources/test-tools/fio/crc/crc64table.h

Purpose: contains the 256-entry NVMe CRC64 lookup table used by the local `fio_crc64_nvme()` implementation.

Important content: `crc64nvmetable` is generated from the NVMe 64-bit CRC polynomial documented in `crc64.c`. It is a header-local `static const unsigned long long` table included by one implementation file.

State and persistence: no mutable state; compile-time constant data only.

Dependencies and integration: included by `crc64.c`; not intended as a broad public API.

Risks and test signals: table corruption would silently break NVMe protection-information checks. Known-answer vectors are the practical validation signal; table formatting itself has little logic to unit test.
