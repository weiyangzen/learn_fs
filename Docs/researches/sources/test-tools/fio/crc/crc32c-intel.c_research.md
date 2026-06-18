## sources/test-tools/fio/crc/crc32c-intel.c

Purpose: Intel SSE4.2 hardware CRC32C implementation with runtime CPUID probing.

Important APIs and flow: defines `crc32c_intel_available`, `crc32c_intel()` when `ARCH_HAVE_SSE4_2` is set, and `crc32c_intel_probe()`. The function processes native word chunks with encoded CRC32 instructions and finishes byte remainders through `crc32c_intel_le_hw_byte()`. The probe checks CPUID leaf 1 ECX bit 20 once.

State and persistence: mutable globals cache availability and probed state. No files.

Dependencies and integration: depends on `crc32c.h`, `do_cpuid`, and `BITS_PER_LONG`. Header dispatch selects this path after ARM64 and before software.

Risks and test signals: inline assembly is sensitive to compiler constraints and 32/64-bit word size. It initializes CRC to `~0` like the software implementation, so hardware and software outputs should match for every vector. CI on SSE4.2-capable x86 plus forced software comparison is the signal.
