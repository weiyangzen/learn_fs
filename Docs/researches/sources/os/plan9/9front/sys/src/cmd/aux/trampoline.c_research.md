# File Research: sources/os/plan9/9front/sys/src/cmd/aux/trampoline.c

`trampoline` connects two byte streams: stdin/stdout or an alternate address to a target dial address. It forks two copy directions and posts a hangup note when one side ends. With `-9`, it preserves 9P message framing by reading the 4-byte length and forwarding whole messages.

Options include `-a` alternate local dial address, `-m` netdir for MAC authorization, `-o` ctl options for the outgoing target, and `-t` inactivity timeout. Timeout mode forks a supervisor that checks an `activity` flag and posts a group timeout note.

MAC checking reads local/remote endpoint files, looks up remote IP in `<net>/arp`, then checks NDB for an `ether=<mac>` entry with `trampok`.
