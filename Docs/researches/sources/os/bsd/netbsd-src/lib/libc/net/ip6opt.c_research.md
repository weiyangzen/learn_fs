# File Research: sources/os/bsd/netbsd-src/lib/libc/net/ip6opt.c

IPv6 Hop-by-Hop and Destination option construction/parsing helpers for both RFC2292 and RFC3542 APIs. The older `inet6_option_*` functions operate on ancillary `cmsghdr` objects, insert Pad1/PadN options, maintain `ip6e_len`, and iterate or search options with strict length checks through `ip6optlen()`.

The newer `inet6_opt_*` functions operate directly on extension-header buffers. They validate 8-byte header sizing, option type/length/alignment constraints, skip padding while iterating, and use byte-copy helpers for unaligned option data values.

`inet6_insert_padopt()` centralizes Pad1 versus PadN encoding for padding lengths.
