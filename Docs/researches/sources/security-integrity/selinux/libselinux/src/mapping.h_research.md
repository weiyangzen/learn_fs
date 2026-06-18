<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.h -->
# sources/security-integrity/selinux/libselinux/src/mapping.h

## Purpose
Declares the internal class/permission mapping interface used by libselinux AVC and string representation code.

## Important APIs, Types, And Functions
The header exposes `unmap_class()`, `unmap_perm()`, `map_class()`, `map_perm()`, and `map_decision()`. These functions convert between userspace mapped values and kernel policy values.

## Control Flow
There is no executable control flow in the header. It defines the contract that callers must use mapped classes at the public boundary and raw kernel classes when talking to selinuxfs.

## State And Persistence Behavior
No state lives in the header; the backing mapping table is process-global in `mapping.c`.

## Dependencies And Integration Points
Includes `selinux/selinux.h` and `selinux/avc.h` so it can name `security_class_t`, `access_vector_t`, and `struct av_decision`.

## Risks And Test Signals
The main risk is ABI drift between declarations and `mapping.c` definitions. Build tests plus AVC/stringrep tests that call all mapping helpers are the meaningful signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/mapping.h -->
