# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/impl/fcgs2.h

Defines FC-GS-2 / FC-CT common transport and name-server constants. It includes CT revision, service type/subtype constants, FC-CT accept/reject codes, reject reasons, name-service command codes, name-service reject explanations, management-service command codes, class-of-service bits, and port type values.

The file provides registration/query payload structures for port/node WWNs, class of service, FC-4 types, symbolic names, port type, IP address, initial process associator, deregistration, `GID_PT`, `GA_NXT`, `GID_PN`, `GPN_ID`, and `GPT_ID`. `ns_resp_gan_t` is the large aggregate response used for discovery.

It also duplicates SCR registration constants used elsewhere. This is the primary name-server protocol layout header used by fp/fctl and ULP name-service paths.
