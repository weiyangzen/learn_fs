# File Research: sources/os/linux/linux-stable/fs/isofs/rock.h

Defines SUSP and Rock Ridge on-disk record structures.

Structures:
- SUSP: SP, CE, ER.
- Rock Ridge: RR, PX, PN, SL and `SL_component`, NM, CL, PL, TF.
- Linux zisofs extension: ZF with algorithm, parameters, and real size.
- `struct rock_ridge` wraps signature, length, version, and a union of record payloads.

Flags:
- TF timestamp flags for create, modify, access, attributes, backup, expiration, effective, and long form.
- RR presence bits for PX, PN, SL, NM, CL, PL, RE, and TF.

The structures use packed/flexible-array layout where needed to match on-disk variable-length fields.
