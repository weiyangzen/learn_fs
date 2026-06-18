# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_ipv4_impl.h

## Role

Shared implementation declarations for IPv4-style tunnel MAC plugins, used by `mac_ipv4`, `mac_6to4`, and `mac_ipv6`.

## Structure

Includes `sys/mac.h` and declares address verification, SAP verification, header construction, header parsing, and plugin-data validation functions: `mac_ipv4_unicst_verify()`, `mac_ipv4_multicst_verify()`, `mac_ipv4_sap_verify()`, `mac_ipv4_header()`, `mac_ipv4_header_info()`, and `mac_ipv4_pdata_verify()`.

## Dependencies And Consumers

Consumed by tunnel MAC plugin implementation files. Depends on MAC header types such as `mac_header_info_t`, `mblk_t`, and `boolean_t`.

## Important Details

Despite the file name, comments state the helpers are shared by 6to4 and IPv6 tunnel plugins as well as the IPv4 plugin.

## Research Notes

Read completely: 55 lines, 1632 bytes.
