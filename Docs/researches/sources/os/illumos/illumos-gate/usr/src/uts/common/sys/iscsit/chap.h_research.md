# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/chap.h

This header defines CHAP validation support for the iSCSI target side.

Key definitions:
- `chap_validation_status_type` covers pass, invalid response, duplicate secret, unknown auth method, internal error, RADIUS access error, bad RADIUS secret, and unknown RADIUS code.
- `authentication_method_type`: RADIUS or direct authentication.
- `RADIUS_CONFIG` stores server address, port, shared secret, and shared secret length.

Function:
- `chap_validate(...)` validates a target CHAP response using target and initiator CHAP names, challenge, response, identifier, selected authentication method, and method-specific config data.

Dependencies:
- Includes `netinet/in.h`, `sys/int_types.h`, `sys/iscsit/iscsi_if.h`, and `sys/iscsit/radius_protocol.h`.

Relevance:
- Authentication/security component for iSCSI target sessions.
