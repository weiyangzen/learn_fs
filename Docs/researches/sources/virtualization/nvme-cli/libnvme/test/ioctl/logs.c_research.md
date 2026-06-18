# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/logs.c

## Purpose
Mock-ioctl test suite for Get Log Page initializer helpers.

## Test Coverage
Covers sanitize, management address list, supported log pages, error, SMART, firmware slot, changed namespace list, command effects, self-test, telemetry host/controller, endurance group, predictable latency, FDP configs/RUH usage/stats/events, ANA, LBA status, endurance group events, FID/MI supported effects, boot partition, rotational media, dispersed namespace participating NVM subsystems, PHY RX EOM, reachability groups/associations, changed allocated namespace list, discovery, host discovery, AVE discovery, pull-model DDC request, media unit status, supported capacity config list, reservation notification, ZNS changed zones, persistent event, and lockdown logs.

## Behavior
Asserts LID, LSP, RAE, NUMD, NSID, CSI, offsets, domain/endurance/NVM-set selectors, and data-copy behavior by comparing mock output payloads to caller buffers.

## Relevance
Protects the command construction layer for diverse NVMe telemetry, health, topology, fabrics, FDP, ZNS, and namespace event logs.
