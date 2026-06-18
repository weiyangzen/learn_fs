# File Research: sources/virtualization/nvme-cli/nvme-rpmb.c

- Purpose: implements nvme-cli RPMB support commands: info, program-key, read-counter, read-data, write-data, read-config, and write-config.
- Crypto path: uses Linux `AF_ALG` sockets for `hmac(sha256)` and `md5`; HMAC authenticates RPMB writes and MD5 seeds request nonces.
- Protocol structures: defines packed RPMB data frames, config blocks, request/response type enums, security protocol constants, and controller RPMB capability bitfield parsing from identify-controller `rpmbs`.
- NVMe transport: sends RPMB frames through Security Send and Security Receive admin passthrough commands with protocol `0xEA` and SPSP `0x0001`.
- Request handling: builds request frames with type, target, nonce, address, sector count, and optional data; reads responses and checks response type, result, nonce, MAC, and write-counter progression.
- Data operations: chunks authenticated reads/writes according to controller access size, validates transfer size against total RPMB size, and writes read data/config blocks to files when requested.
- Config operations: reads and writes the device configuration block, including boot partition protection and lock status display.
- CLI integration: `rpmb_cmd_option()` parses keys from inline string or file, data from inline string or file, target/address/block options, opens the device, identifies RPMB support, and dispatches the chosen RPMB action.
- Risks and notes: key sizes are limited to 1..223 bytes; file writes append with `ab+`; randomness for nonce is based on `rand()` hashed with MD5, not a cryptographic RNG.
