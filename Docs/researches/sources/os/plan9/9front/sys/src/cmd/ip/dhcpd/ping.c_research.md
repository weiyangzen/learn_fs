# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/ping.c

ICMP probe used before handing out dynamic leases. `icmpecho` sends up to three IPv4 echo requests with a fixed payload and short alarm timeout, returning true if a matching echo reply arrives.

Non-IPv4 addresses are treated as not answering. The DHCP server uses this to avoid reassigning addresses that still respond despite expired lease state.
