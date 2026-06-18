# sources/user-network-fs/samba/source3/printing/rap_jobid.h

## Purpose

`rap_jobid.h` declares the legacy RAP-to-spoolss print job ID mapping API.

## Important APIs, Types, and Functions

- `pjobid_to_rap(const char *sharename, uint32_t jobid)` maps a 32-bit spoolss job to a 16-bit RAP ID.
- `rap_to_pjobid(uint16_t rap_jobid, fstring sharename, uint32_t *pjobid)` resolves a RAP ID.
- `rap_jobid_delete(const char *sharename, uint32_t jobid)` removes a mapping.

## Control Flow

The header exposes a simple create-or-find, resolve, and delete lifecycle for print job ID compatibility.

## State and Persistence

No state is defined in the header; the implementation owns an in-memory TDB and allocation counter.

## Dependencies and Integration Points

It includes `includes.h` for Samba types such as `fstring` and integer typedefs. `printing.c` and `printspoolss.c` are primary consumers.

## Risks and Edge Cases

The API returns `0` for failure from `pjobid_to_rap()`, making zero an invalid RAP ID by contract. Callers must treat false from `rap_to_pjobid()` as lookup failure.

## Test Signals

Header coverage is mostly compile-time; integration tests should verify consumers correctly handle `0` and false lookup results.
