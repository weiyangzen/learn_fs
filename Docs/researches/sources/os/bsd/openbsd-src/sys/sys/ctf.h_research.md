# File Research: sources/os/bsd/openbsd-src/sys/sys/ctf.h

This header defines the Compact C Type Format ABI structures and encoding macros.

Key definitions:
- File/layout structs: `ctf_header`, `ctf_lblent`, `ctf_stype`, `ctf_type`, `ctf_array`, `ctf_member`, `ctf_lmember`, `ctf_enum`.
- Format constants: `CTF_MAGIC`, `CTF_VERSION`, `CTF_F_COMPRESS`, `CTF_MAX_NAME`, `CTF_MAX_VLEN`, `CTF_MAX_SIZE`, `CTF_LSIZE_SENT`.
- Type-kind macros: `CTF_INFO_VLEN`, `CTF_INFO_ISROOT`, `CTF_INFO_KIND`, and `CTF_K_*`.
- Integer/float encoding macros and flags.
- String-table/name and large-size/member-offset helpers.

Behavior and integration:
- Describes the on-disk/in-object CTF ABI; no functions are declared.
- Large structs use `CTF_LSTRUCT_THRESH` and `ctf_lmember` high/low offset fields.

Risk notes:
- All offsets and sizes are ABI layout fields; changes require matching consumers such as debuggers, linkers, or CTF readers.
- Macro aliases like `ctt_name` and `ctlm_name` intentionally overlay embedded structs for compact layout.
