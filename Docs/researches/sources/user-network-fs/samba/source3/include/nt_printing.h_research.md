# sources/user-network-fs/samba/source3/include/nt_printing.h

## Purpose
`nt_printing.h` declares NT spoolss-facing printing support: printer metadata, driver architecture mapping, driver file validation/copying, printer publishing, access checks, GUID storage, and spoolss notification data structures. It bridges Samba print shares to Windows printing semantics.

## Important APIs, Types, And Control Flow
Constants describe DOS, NE, PE, and version-resource header offsets used for driver inspection. `SPOOLSS_NOTIFY_MSG`, group, and container structs represent spoolss change notifications. `PRINTER_ATTRIBUTE_SAMBA` and `PRINTER_ATTRIBUTE_NOT_SAMBA` define Samba-owned versus network printer attributes. `struct print_architecture_table_node` maps long spoolss architecture strings to short driver directory names and versions; the static `archi_table` includes Win40, x86, MIPS, Alpha, PPC, IA64, x64, and ARM64 entries. Functions initialize printing, translate architecture strings, check access/time windows, retrieve/store/get printer GUIDs, publish and inspect printers, check drivers/files in use, delete driver files, move/clean driver upload structures, and add/remove printer records.

## State And Persistence
Persistent state includes printer GUIDs, published printer state, driver files in download areas, registry/spoolss printer records, and notification messages sent through Samba messaging. The header's static architecture table is compile-time state included in each translation unit that includes it.

## Dependencies And Integration Points
It depends on generated spoolss NDR, `messaging_context`, auth session info, GUIDs, WERROR, DCERPC binding handles, printer service numbers, and spoolss driver info structures. It integrates with printing backends, Samba registry printing keys, Active Directory printer publishing, driver upload paths, and access-control checks.

## Risks And Test Signals
Risks include PE/NE parser offset mistakes, static table duplication, incomplete architecture grouping for enumdrivers, deleting driver files still in use, printer GUID inconsistency, and access checks that diverge from spoolss expectations. Test signals include driver upload/cleanup for each architecture, PE version parsing, printer publish/unpublish, GUID persistence, print admin versus user access checks, deletion while drivers are referenced, notification delivery, and enumdrivers grouping behavior.
