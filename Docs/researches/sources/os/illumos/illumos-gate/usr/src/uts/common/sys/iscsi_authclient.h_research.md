# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclient.h

This header defines the Cisco-derived iSCSI authentication client interface, mainly for CHAP authentication negotiation.

Limits and constants:
- String, string-block, and large-binary maximum lengths.
- Receive-end max count.
- Client signature.
- CHAP response length.
- Key type enum for AuthMethod, CHAP algorithm, username, response, identifier, and challenge.

Enums:
- Authentication options: reject, not present, none, CHAP, MD5 algorithm.
- Negotiation role: originator/responder.
- Version: draft8 or RFC.
- Status: no error, error, pass, fail, continue, in progress.
- Detailed debug status values for success/failure, bad/missing keys, password issues, duplicate keys, string/data limits, T-bit issues, and receive limits.
- Node type: initiator/target.
- Auth phase: configure, negotiate, authenticate, done, error.
- Local and remote CHAP negotiation state machines.

Structures:
- `IscsiAuthClientGlobalStats`.
- Buffer/key descriptors: `IscsiAuthBufferDesc`, `IscsiAuthKey`, `IscsiAuthLargeBinaryKey`, `IscsiAuthKeyBlock`, `IscsiAuthStringBlock`, `IscsiAuthLargeBinary`.
- `IscsiAuthClient` is the main authentication state object, storing config, method/algorithm lists, username/password, version, challenge policy, callbacks, phase/state, debug status, negotiated values, CHAP challenge/response state, and send/receive key blocks.

APIs:
- Init/finish; receive begin/end.
- Key name/type lookup and iteration.
- Receive/send key-value and transit bit handling.
- Set methods, role, algorithms, username/password, remote auth, glue handle, method-list name, IPsec/base64, challenge length, version.
- Query password need, auth phase/status/method/algorithm/username/debug status.
- Send status code and convert debug status to text.
- Platform callback `iscsiAuthClientAuthResponse`.
- Platform-dependent hooks for CHAP auth request/cancel, text-number conversion, random data, MD5 operations, and data encoding/decoding.

Dependencies:
- Includes `sys/iscsi_authclientglue.h`, which provides MD5 context typing.

Relevance:
- Authentication layer for iSCSI sessions. Directly relevant to network block storage security and login behavior.
