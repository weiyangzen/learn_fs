## sources/test-tools/fio/crc/crc64.c

Purpose: provides fio's generic CRC64 and NVMe CRC64 implementations.

Important APIs and flow: `fio_crc64()` uses a local table for polynomial `0x95AC9329AC4BC9B5` and initial zero, consuming bytes with right shifts. `fio_crc64_nvme()` either calls ISA-L `crc64_rocksoft_refl()` when `CONFIG_LIBISAL64` is set or uses `crc64nvmetable` with one's-complement seed/final handling for incremental NVMe CRC64.

State and persistence: no mutable state; tables are static constant data.

Dependencies and integration: includes `crc64.h`, `crc64table.h`, and optionally ISA-L `<isa-l/crc64.h>`. Used by verification/checksum paths and CRC tests.

Risks and test signals: the generic and NVMe CRC64 variants have different polynomials/initialization. ISA-L and local implementations must match. Known-answer NVMe vectors and software/ISA-L parity tests are important.
