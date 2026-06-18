# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat_y.y

This is the yacc grammar and parser-side loader for `ipnat` NAT rules. It parses `map`, `map-block`, `bimap`, `rdr`, `rewrite`, `divert`, proxy configuration, variable assignment, address forms, pool/hash lookups, port ranges, protocol selectors, NAT tags, age, fragment, sticky, purge, MSS clamp, and IPv4/IPv6 family annotations.

Parsed rules are accumulated as dynamically sized `ipnat_t` records. `newnatrule()` initializes a rule, `addname()` appends interface/proxy/config names into the variable-sized rule name area, and after each grammar rule the parser calls the supplied add function, normally `ipnat_addrule()`. `ipnat_addrule()` wraps rules in `ipfobj_t` and dispatches the relevant ioctl: add, remove, purge, or zero rule counters depending on global `opts`.

The grammar does substantial semantic validation: address-family mismatch checks, port/protocol consistency, redirect destination mask constraints, pool/hash usage restricted to `from/to` filters, and automatic protocol inference when a port is present. `setnatproto()`, `setmapifnames()`, and `setrdrifnames()` normalize protocol flags, interface indexes, and map-block/autoportrange behavior before kernel submission.

Proxy handling is embedded. DNS proxy config blocks are parsed through a temporary fixed dictionary, converted into `proxyrule_t`/`namelist_t` lists, and submitted with `SIOCPROXY` after NAT rules are loaded.

Important dependencies include `ipf.h`, `netinet/ipl.h`, `ipnat_l.h`, the common lexer/reset/variable APIs, host and service resolution helpers, `nat_setgroupmap()`, `printnat()`, `binprint()`, and IPFilter ioctl constants.

Implementation notes and risks:
- Parser state is global (`nat`, `nattop`, `prules`, `natfd`, `suggest_port`), so parsing is not reentrant.
- `addname()` reallocates the active `ipnat_t`; callers must use the updated pointer.
- Some error paths call `yyerror()` but continue semantic actions, matching old yacc style.
- The grammar mutates lexer dictionaries and global address-expectation flags, making rule ordering and reset paths important.
