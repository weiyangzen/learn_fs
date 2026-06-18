# File Research: sources/os/plan9/9front/sys/src/9/pc/segdesc.c

## Role

Architecture debug/control file support for reading and writing per-process x86 GDT and LDT segment descriptors through `/dev/arch` files.

## Main Interfaces

- `segdesclink()` registers arch files `gdt` and `ldt`.
- `gdtread/gdtwrite` operate on the process GDT slots.
- `ldtread/ldtwrite` operate on the process LDT allocation.

## Key Behavior

- Defines textual descriptor types and flag templates for data, code, TSS, LDT, call gates, task gates, interrupt gates, and trap gates.
- Text record format is fixed-width: index, type, flags, DPL, base, and limit.
- `descread()` decodes `Segdesc` entries into type/flag strings.
- `descwrite()` parses records, constructs descriptor words, grows the LDT as needed, updates descriptors, and flushes the MMU for the current process.

## Dependencies And Assumptions

- Depends on x86 descriptor constants such as `SEGP`, `PROCSEG0`, and `NPROCSEG`.
- Write path rejects present system segments unless they are user DPL 3 code/data segments.
- LDT indices are capped below 8192.

## Research Notes

- This is not normal memory-management setup code; it is a controlled inspection/modification interface.
- Permission checks are important because descriptor writes can otherwise install privileged gates or system segments.
