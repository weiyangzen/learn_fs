# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_normalize/npfext_normalize.c

## Summary
Implements userland parameter parsing for the NPF `normalize` extension.

## Main Responsibilities
- Construct extension objects named `normalize`.
- Accept boolean options `random-id` and `no-df`.
- Accept numeric options `min-ttl` and `max-mss`.
- Store recognized parameters through `npf_ext_param_bool()` or `npf_ext_param_u32()`.
- Reject unknown parameters or missing required values with `EINVAL`.

## Risks
Numeric values are parsed with `atol()` and are not range-checked here beyond required presence. Invalid numeric text can collapse to zero.
