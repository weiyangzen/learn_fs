# sources/test-tools/fio/verify.h

Purpose: public definitions for fio verification modes, verify headers, checksum-specific private header payloads, and exported verify APIs.

Important APIs/types: `FIO_HDR_MAGIC`, `VERIFY_HEADER_VERSION`, `enum VERIFY_*` modes, `VERIFY_POLICY_*` bits, `struct verify_header`, and `vhdr_*` checksum payload structs. Declares write-population, next-verify selection, sync/async verification, pattern filling, verifier initialization, async thread lifecycle, and pattern format callback `paste_blockoff()`.

Control flow/state: the common header precedes optional checksum payload and data for most verify modes. `VERIFY_PATTERN_NO_HDR` is explicitly headerless. The high bit in the version distinguishes versioned headers from older formats.

Dependencies/integration: includes `verify-state.h` and compiler annotations. Consumed by fio IO path, ZBD code, trim handling, and state save/load users.

Risks/test signals: enum value changes can affect media compatibility; header layout is on-disk/on-media ABI. Tests should ensure `__hdr_size()` expectations match these structs and that old configurations mapping `verify=meta` to header-only remain compatible.
