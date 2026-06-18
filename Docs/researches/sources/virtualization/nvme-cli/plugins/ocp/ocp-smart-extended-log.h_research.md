# File Research: sources/virtualization/nvme-cli/plugins/ocp/ocp-smart-extended-log.h

## Role

`ocp-smart-extended-log.h` declares the OCP SMART / Health Information Extended C0 log page layout and the `ocp_smart_add_log()` command entry point.

## Data Layout

`struct ocp_smart_extended_log` maps the 512-byte C0 SMART cloud attributes payload. It includes:

- 128-bit physical media units written/read;
- raw and normalized bad NAND block counts;
- XOR recovery, uncorrectable read, soft ECC, end-to-end error, system data, refresh, erase count, thermal throttling, PCIe, shutdown, free block, capacitor, unaligned I/O, security, NUSE, PLP, and endurance metrics;
- OCP/DSSD and NVMe errata/version fields;
- media die health, max temperature, form factor, NAND erase count, command timeout, system-area failure counters;
- power capability/consumption fields;
- DSSD firmware revision, build UUID, and build label;
- die-in-use bad NAND block fields;
- reserved space, log page version, and log page GUID.

The field comments annotate byte ranges and make this header the central contract for both C0 retrieval and all SMART print backends.

## API Surface

The file forward declares `struct command` and `struct plugin`, then declares:

`int ocp_smart_add_log(int argc, char **argv, struct command *acmd, struct plugin *plugin);`

## Dependencies

It includes `<nvme/types.h>` for fixed-width NVMe integer types and `common.h` for shared nvme-cli helpers/macros.

## Notable Risks And Edge Cases

- The struct is not explicitly marked `__packed` in this header, unlike several OCP structs in `ocp-nvme.h`; its correctness depends on natural layout matching the 512-byte wire format on supported compilers.
- Comments and field names contain spelling mistakes such as `shoutdowns`, `errate`, and `noralized`; these names are now part of the C API used by printers.
- Print code reads some byte arrays as integer pointers, so alignment and strict-aliasing assumptions matter.
- Future C0 log page revisions require coordinated updates to this layout and both stdout/JSON printers.
