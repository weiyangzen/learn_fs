# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dls_mgmt.h

## Scope

Complete file read, 242 lines. This header defines data-link management classes, media filters, attributes, and the door upcall ABI used between kernel DLS and `dlmgmtd`.

## Public Surface

It defines `datalink_class_t` values for physical links, VLANs, aggregations, VNICs, etherstubs, simnet, bridge, IP tunnel, partition, overlay, and miscellaneous links, plus `DATALINK_CLASS_ALL`.

It defines `datalink_media_t`, `DATALINK_ANY_MEDIATYPE`, and `DATALINK_MEDIA_ACCEPTED()`. It defines link attribute names `FPHYMAJ`, `FPHYINST`, and `FDEVNAME`, and door paths `DLMGMT_TMPFS_DIR` and `DLMGMT_DOOR`.

Door command constants cover create, getattr, destroy, getname, getlinkid, getnext, update, link property init, and set zone id. Flags describe active, persistent, and transient links.

It exports door argument and return structures for create/destroy/update/getattr/getname/getlinkid/getnext/linkprop-init/setzoneid and corresponding return values.

## Behavior And Integration

The kernel uses this ABI to ask the data-link management daemon to create, destroy, update, find, iterate, and zone data links. Several structures include explicit padding to keep layout identical on amd64 and i386.

## Dependencies And Invariants

The door protocol depends on the first `ld_cmd`/`lr_err` fields being readable for dispatch and status. Structure sizes must remain 32-bit/64-bit compatible. `DATALINK_MEDIA_ACCEPTED()` interprets the high 32 bits as flags and low 32 bits as media value.

## Risks

Door ABI changes must be coordinated with `dlmgmtd`. String fields are fixed-size; callers must enforce termination and bounds. The macro name `lr_paddding` is misspelled in a comment only, but padding fields are required for ABI stability.
