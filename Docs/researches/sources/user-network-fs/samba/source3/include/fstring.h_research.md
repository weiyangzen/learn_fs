# sources/user-network-fs/samba/source3/include/fstring.h

## Purpose
`fstring.h` defines Samba's fixed-size short string type used widely in older source3 structures.

## Important APIs, Types, And Functions
- `FSTRING_LEN` defaults to `256` unless already defined.
- `typedef char fstring[FSTRING_LEN]` defines the storage type.

## Control Flow
No executable flow. Including modules allocate `fstring` fields on stack or inside structs.

## State And Persistence
`fstring` is inline fixed storage. It may be serialized indirectly when embedded in protocol or database structures elsewhere.

## Dependencies And Integration Points
This header is included by `includes.h` and therefore reaches many source3 files. `client.h` uses `fstring` in `print_job_info`.

## Risks
Fixed-size buffers require careful bounded formatting/copying. Redefining `FSTRING_LEN` before inclusion changes ABI for structures containing `fstring`.

## Test Signals
Static analysis and tests should verify bounded writes into `fstring`, truncation behavior, and ABI consistency across modules.
