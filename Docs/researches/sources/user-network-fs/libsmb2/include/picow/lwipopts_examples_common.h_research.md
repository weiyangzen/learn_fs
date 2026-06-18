# sources/user-network-fs/libsmb2/include/picow/lwipopts_examples_common.h

## Purpose
This header supplies common lwIP settings for Pico W examples.

## Important APIs, Types, and Functions
It defaults `NO_SYS` to `1` and `LWIP_SOCKET` to `1`, sets memory and pbuf sizes, enables ARP/Ethernet/ICMP/raw/DHCP/IPv4/TCP/UDP/DNS/keepalive, configures TCP window/send buffer/queue lengths, and turns most lwIP debug categories off. In non-`NDEBUG` builds it enables lwIP debug/statistics.

## Control Flow
No direct code flow. lwIP uses these macros to include protocol features, memory pools, checksums, DHCP behavior, and debug support.

## State and Persistence Behavior
It controls lwIP heap/pool sizing (`MEM_SIZE`, `MEMP_NUM_TCP_SEG`, `PBUF_POOL_SIZE`) and statistics state. No filesystem persistence.

## Dependencies and Integration Points
It integrates with Pico W network examples and `lwipopts.h`. The memory sizing directly affects libsmb2 socket throughput and ability to handle SMB packet bursts.

## Risks and Edge Cases
`MEM_SIZE` of 4000 and `PBUF_POOL_SIZE` of 24 are small relative to SMB workloads, especially large reads/writes or signing/encryption. `MEM_LIBC_MALLOC` depends on `PICO_CYW43_ARCH_POLL`, so allocator behavior differs by architecture mode.

## Test Signals
Run long directory listings and read/write workloads, track lwIP stats in debug builds, and check DHCP/DNS/connect reliability after repeated reconnects.
