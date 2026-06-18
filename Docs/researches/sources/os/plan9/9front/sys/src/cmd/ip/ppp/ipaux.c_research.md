# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/ipaux.c

PPP checksum helpers. `ptclcsum` computes a protocol checksum over a `Block` slice using `ptclbsum`, bounded by block length, and returns the complemented 16-bit result. `ipcsum` computes the IPv4 header checksum over the header length encoded in the first byte.
