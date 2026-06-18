# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/usbd.c

## Role

Implements the `usbd` 9P service, USB attach/detach event stream, hub control file, stable device naming, and daemon startup.

## 9P Interface

The service exposes:

- `usbevent`: read-only attach/detach event stream.
- `usbhubctl`: write-only hub port control.

Readers of `usbevent` are ordered and each event is claimed by one reader at a time using `Dev->aux`. On open, existing non-hub configured devices are enumerated into the reader’s event chain.

`usbhubctl` accepts commands for `portpower` and `portindicator`, finds hubs by hardware name or numeric id, validates port and capability support, then calls `portfeature`.

## Event Model

`pushevent` appends events with device references. `procreqs` advances readers, claims devices, and fulfills pending reads. `detachdev` and `attachdev` publish formatted events of the form `attach/detach id vid did csp hname`.

## Device Naming And Startup

`assignhname` builds a stable identity string from VID, DID, device revision, class/subclass/protocol, and serial string, hashes it through `hname`, and resolves collisions with numeric suffixes.

`main` initializes formatting, creates root hubs from `/dev/usb` or explicit arguments, creates `/env/usbbusy`, and posts the service. The service start hook forks `work` to run hub polling.

## Notable Details

`attachdev` creates default configuration endpoint files before publishing the attach event. `checkidle` removes `/env/usbbusy` once event readers have consumed initial enumeration.
