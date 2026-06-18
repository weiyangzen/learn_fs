# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/ipf_y.y

## Purpose
Yacc grammar and semantic actions for parsing IPFilter rule files and applying parsed rules.

## Main Elements
- Defines tokens and grammar for `ipf.conf` syntax: `pass`, `block`, `count`, `auth`, `preauth`, `call`, `skip`, `log`, `quick`, `on`, `dup-to`, `route-to`, `reply-to`, `from`, `to`, `with`, `keep state`, `keep frags`, tags, pools, hashes, BPF, expressions, IPv4/IPv6 options, ICMP types/codes, syslog levels, and tunables.
- Maintains parser state in globals such as `fr`, `frc`, `frtop`, `frold`, `ipffd`, `ipfioctls`, and `ipfaddfunc`.
- Expands list syntax into multiple `frentry_t` rules with `addrule()`.
- Builds normal IPF match data, BPF opcode match data, and expression match data.
- Supports inline anonymous pools/hashes by loading them through lookup ioctls.
- Adds/removes/zeros rules through `ipf_addrule()` and ioctl commands selected from global `opts`.
- Provides keyword dictionaries used by the hand-written lexer.

## Dependencies And Integration
Generated into `ipf_y.c` by `ipf/ipf/Makefile`; paired with the transformed lexer as `ipf_l.c`. Used by `ipf_parsefile()` / `ipf_parsesome()` from the `ipf` command and shared `libipf` paths.

## Risk Notes
The semantic actions directly allocate, clone, mutate, and submit kernel ABI structures. Parser-state globals make the code sensitive to reentrancy assumptions. `do_tuneint()` appears to overwrite its `name=value` buffer with only the numeric value before calling `ipf_dotuning()`, which is a notable maintenance risk.
