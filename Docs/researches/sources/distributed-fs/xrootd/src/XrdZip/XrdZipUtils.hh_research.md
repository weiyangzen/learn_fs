# sources/distributed-fs/xrootd/src/XrdZip/XrdZipUtils.hh

Purpose: Defines common XrdZip utility types and byte-conversion helpers used by ZIP record classes. The file centralizes little-endian serialization/deserialization, an overflow sentinel template, a ZIP buffer alias, and DOS timestamp construction.

Important APIs/types/functions: `XrdZip::bad_data` is a marker exception for corrupted ZIP input. `ovrflw<UINT>::value` returns the all-ones unsigned sentinel used where ZIP32 fields overflow into ZIP64. `buffer_t` is `std::vector<char>`. `copy_bytes`, `from_buffer`, and `to` move integer values to and from raw buffers, applying `bswap` on `Xrd_Big_Endian`. `dos_timestmp` stores packed DOS `time` and `date` fields and builds them from current time or a supplied `time_t`.

Control flow: Serialization helpers reinterpret integer storage as bytes, reverse on big-endian hosts, and append/read fixed-width fields. Timestamp constructors call `std::localtime`, mask calendar fields, and shift them into ZIP DOS bit positions.

State and persistence behavior: No persistent state is owned. The helpers mutate caller-provided buffers or pointer cursors. `dos_timestmp` stores two 16-bit packed values intended to be persisted inside ZIP metadata.

Dependencies and integration points: Depends on `XrdSysPlatform.hh` for platform endian definitions and `bswap`. ZIP headers such as EOCD, ZIP64 EOCD, and locator structures use these functions to remain endian-correct.

Risks: The deserialization helpers assume the source buffer is large enough and correctly aligned for `memcpy` length; callers must validate sizes. `std::localtime` returns local calendar time and may be thread-hostile on some platforms. Month packing uses `tm_mon` directly, which is zero-based in C but DOS dates are normally one-based, so timestamp consumers should verify expectations.

Test signals: Useful tests are endian round trips for all integer widths, malformed short-buffer handling at callers, and fixed `time_t` conversion cases around month/year boundaries.
