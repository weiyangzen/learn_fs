# File Research: sources/virtualization/nvme-cli/plugins/dera/dera-nvme.c

- Purpose: Dera vendor plugin for device status and additional SMART-like health fields.
- Log layout: defines `nvme_dera_smart_info_log` with rebuild counters, capacitor health, NAND/DDR/PCIe error counters, power fields, firmware strings, voltage counters, temperature sensor counters, and reserved padding.
- Status command: retrieves log page `0xC0`, then sends admin passthrough opcode `0xC0` with `cdw12=0x104` to obtain current device status.
- Output: prints status strings, rebuild progress where applicable, capacitor state/voltage, NAND errors, power level/current power, PCIe voltage status, temperature abnormal count, NAND retry failures, and firmware slot version.
- Registration: exposed as `smart-log-add` with alias `stat`.
