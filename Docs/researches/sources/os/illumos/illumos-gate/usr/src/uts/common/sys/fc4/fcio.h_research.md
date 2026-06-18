# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fcio.h

## Role

`fcio.h` defines FC/FC-AL ioctl payloads, maps, link-status structures, firmware/microcode version buffers, and kstat/statistics structures for SOCAL and IFP-style Fibre Channel adapters.

## Ioctls And Maps

- Defines `FIOC`, `SF_IOC`, `SFIOCGMAP`, `SF_NUM_ENTRIES_IN_MAP`, and FC ioctls for limited map, force LIP, link status, and FCode/microcode/prom versions.
- Provides IFP compatibility aliases for map, force LIP, and link status commands.
- `sf_al_addr_pair_t` stores AL_PA, hard address, inquiry dtype, node WWN, and port WWN.
- `sf_al_map_t` stores device count, 127 address pairs, and HBA address.
- Defines `rls_payload`, `lilpmap`, and `socal_fm_version`.

## Statistics And Status Codes

- Defines target stats for ELS failures, timeouts, ABTS failures, task management failures, RO/length mismatches, and received LOGOs.
- Defines `sf_stats_t`, `fc_pstats`, `socal_stats_t`, IFP target stats, and `ifp_stats_t`.
- Defines FCAL response status codes for OK, rejects/busies, online/offline/timeout/overrun, loop state, old/al port, queue/exchange errors, abort/diagnostic/DMA/CRC/open failures, generic error, online timeout, and max status.
- Defines QLA21xx/IFP command completion status codes such as complete, incomplete, DMA error, transport error, reset, aborted, timeout, overrun/underrun, abort/reset rejected, queue full, port unavailable/logged out, and port config changed.
