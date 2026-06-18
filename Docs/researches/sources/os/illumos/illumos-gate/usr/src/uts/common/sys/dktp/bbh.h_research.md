# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dktp/bbh.h

## Scope

Complete file read, 81 lines. This header defines the DKTP bad-block handling object interface.

## Public Surface

The header includes `sys/scsi/scsi_types.h` and exports:

- `struct bbh_cookie`: sector address and contiguous sector length for bad-block handling.
- Address aliases `ck_lsector` and `ck_sector` into `lldaddr_t`.
- `bbh_cookie_t`.
- `struct bbh_handle`: cookie table plus current index/count.
- `struct bbh_obj`: object data pointer plus operation table.
- `struct bbh_objops`: callbacks for init/free, mapping a `buf` into a handle, converting handle to cookie, and freeing a handle.
- Dispatch macros `BBH_INIT`, `BBH_FREE`, `BBH_GETHANDLE`, `BBH_HTOC`, and `BBH_FREEHANDLE`.
- Cookie accessor macros `BBH_GETCK_SECTOR` and `BBH_GETCK_SECLEN`.

## Behavior And Integration

The file implements object-style polymorphism with function pointers and macros. Common disk drivers can call bad-block handlers without knowing the concrete implementation. The handler translates I/O buffers into one or more physical-sector cookies, allowing remap/alternate-sector logic to participate in strategy paths.

## Dependencies And Invariants

It depends on DKTP/SCSI opaque types, `struct buf`, and `lldaddr_t`. The object pointer passed to macros must be a valid `struct bbh_obj *` with a populated `bbh_ops` table.

## Risks

The dispatch macros perform unchecked casts and dereference callbacks directly. A missing callback or wrong object type will fail at runtime. The `ck_sector` alias accesses only the `_p._l` member of `lldaddr_t`, so large-sector users must ensure they use the correct address alias.
