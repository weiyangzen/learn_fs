# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf.h

## Purpose
Central userland IPFilter header for shared types, compatibility includes, global variables, and function declarations.

## Main Elements
- Pulls in system socket/IP headers plus IPFilter kernel/user structures such as `ip_fil`, `ip_nat`, `ip_state`, `ip_pool`, `ip_htable`, `ip_dstlist`, and related headers.
- Defines compatibility typedefs and utility macros.
- Defines shared parser/helper structs: `ipopt_names`, `alist_t`, `plist_t`, `fakebpf_t`, `icmptype_t`, `wordtab_t`, `namelist_t`, and `proxyrule_t`.
- Declares common callback types for ioctl, add-rule, and copy operations.
- Exposes parser globals such as `use_inet6`, `lineNum`, and `debuglevel`.
- Declares many shared helper APIs for address parsing, rule parsing, NAT parsing, pool/hash loading, printing, error reporting, lexer variables, debugging, and state/NAT formatting.

## Dependencies And Integration
Included by most IPFilter userland tools and generated parser/lexer sources. It bridges userland utilities to the kernel IPFilter ABI.

## Risk Notes
This header is a broad coupling point. ABI or structure changes in the kernel IPFilter headers can ripple through nearly every IPFilter userland program.
