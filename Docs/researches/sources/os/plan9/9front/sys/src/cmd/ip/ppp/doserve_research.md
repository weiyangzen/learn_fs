# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ppp/doserve

Tiny rc helper for PPP service-side testing. It binds IP stack `#I1` onto `/net.alt`, starts `ndb/cs` for `.alt`, and runs `aux/listen` on `/net.alt/tcp` with `/rc/bin/service`.
