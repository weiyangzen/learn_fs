# File Research: sources/virtualization/nbdkit/filters/ip/rules.c

Parses, stores, prints, and evaluates IP filter rules. Rule types include any/all, IPv4/IPv6, CIDR prefixes, loopback variants, Unix sockets, TLS DN and issuer-DN globs, peer pid/uid/gid, security context, and vsock CID/port.

`parse_rules()` splits comma lists except for DN-style rules, while `parse_rule()` recognizes symbolic names, identity prefixes, security labels, CIDR addresses, and bare IP addresses. DN and issuer-DN rules set `late_filtering`.

Matching uses `nbdkit_peer_name()` to obtain a `sockaddr`, then tests rules in list order. IPv4 CIDR uses host-order masks; IPv6 prefix matching is bytewise. TLS DN matching uses `fnmatch()` with case folding when available. Unix peer metadata and security context are obtained through nbdkit peer helpers.

`check_if_allowed()` fails closed if peer name lookup fails, logs peer/rule matching under `-D ip.rules=1`, gives allow rules precedence, then deny rules, then default allow.
