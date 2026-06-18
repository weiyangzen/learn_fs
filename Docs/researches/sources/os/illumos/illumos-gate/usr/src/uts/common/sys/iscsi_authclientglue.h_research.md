# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclientglue.h

This small header provides platform glue for the iSCSI auth client.

Key definitions:
- Includes `<md5.h>`.
- `typedef MD5_CTX IscsiAuthMd5Context;`
- Declares global handles:
  - `iscsiAuthIscsiServerHandle`
  - `iscsiAuthIscsiClientHandle`

Purpose:
- Decouples the generic auth client from the platform MD5 context type and platform-specific handle storage.

Relevance:
- Support header for iSCSI CHAP authentication.
