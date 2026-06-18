# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucExport.hh

## Purpose
Declares export option bit definitions and the `XrdOucExport` parsing helpers.

## Important APIs, Types, And Functions
The header defines low-half setting bits and high-half explicit-mask bits such as `XRDEXP_READONLY`, `XRDEXP_FORCERO`, `XRDEXP_NODREAD`, `XRDEXP_STAGE`, `XRDEXP_MIG`, `XRDEXP_MMAP`, `XRDEXP_MLOK`, `XRDEXP_MKEEP`, `XRDEXP_PURGE`, `XRDEXP_NOXATTR`, `XRDEXP_INPLACE`, `XRDEXP_PFCACHE`, `XRDEXP_LOCAL`, `XRDEXP_GLBLRO`, `XRDEXP_NOFICL`, plus aggregate masks `XRDEXP_SETTINGS`, `XRDEXP_MEMAP`, and `XRDEXP_MIGPRG`. Static methods are `ParseDefs` and `ParsePath`.

## Control Flow
No runtime logic in the header beyond declarations. Consumers pass config streams and export-list anchors to the static parser functions.

## State And Persistence
Defines policy flags only. Parsed state lives in `XrdOucPList` instances maintained by callers.

## Dependencies And Integration Points
Includes `XrdSysError.hh`, `XrdOucPList.hh`, and `XrdOucStream.hh`. The bit layout is shared with configuration, namespace export, cache, staging, migration, and access-control code.

## Risks And Test Signals
Changing flag values or mask positions can break persisted assumptions across modules. `XRDEXP_NOLK` is currently zero because lock options are prescreened elsewhere, so callers must not infer a stored lock bit. Compile and config-parser regression tests are key signals.
