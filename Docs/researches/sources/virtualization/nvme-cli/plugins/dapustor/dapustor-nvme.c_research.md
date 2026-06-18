# File Research: sources/virtualization/nvme-cli/plugins/dapustor/dapustor-nvme.c

- Purpose: DapuStor vendor plugin for additional SMART log retrieval and decoding.
- Data layout: defines packed SMART log item unions for raw 48-bit counters, wear-level triples, thermal throttle fields, temperature triples, power consumption triples, and extended SMART attributes.
- Log retrieval: reads vendor log `0xCA` for base additional SMART and attempts log `0xCB` for extended SMART; absence of extended log is tolerated.
- Output modes: supports normal text, JSON, and raw binary.
- Decoded metrics: includes program/erase fail counts, wear leveling, E2E/CRC errors, timed workload metrics, thermal throttle, NAND/host bytes, system-area life, NAND reads, temperature/power stats, power-loss protection, read failures, media errors, write amplification, firmware update count, DRAM ECC, XOR counts, inflight I/O, and lifetime/boot temperature ranges.
- CLI: command parses namespace, raw-binary, JSON/global output options and uses common parse/open and print helpers.
