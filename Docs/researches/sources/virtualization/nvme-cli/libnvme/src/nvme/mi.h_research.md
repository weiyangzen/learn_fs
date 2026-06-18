# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.h

Public NVMe Management Interface API for libnvme-mi.

Key API areas:
- Documents MI topology:
  - endpoint represents the remote MI-capable management endpoint
  - controller transport handles represent NVMe controllers behind an endpoint
- Defines `libnvme_mi_ep_t`.
- Endpoint operations:
  - set CSI bit
  - iterate endpoints in a global context
  - set/get timeout
  - set MPRT maximum wait
  - open MCTP endpoint
  - close endpoint
  - scan MCTP via D-Bus
  - scan endpoint for controllers
  - create controller transport handle
  - get controller ID
  - describe endpoint
- MI tracing hooks:
  - endpoint submit-entry callback
  - endpoint submit-exit callback
  - weak global submit-entry/exit hooks
- MI command API:
  - raw MI transfer
  - Read MI Data subsystem, port, controller list, controller info
  - Subsystem Health Status Poll
  - Configuration Get/Set
  - inline helpers for SMBus frequency, MCTP MTU, and health status change clearing
  - async event configuration get/set and ACK helper
- Admin channel:
  - raw Admin transfer over MI.
- Control primitive:
  - `libnvme_mi_control()`.
- AEM API:
  - handler next-action enum
  - event structure
  - enabled-map structure
  - AEM config structure
  - get pollable fd
  - enable/get-enabled/disable/process
  - iterate event payloads during callback

Research notes:
- The header explicitly separates endpoint-level MI commands from controller-targeted Admin commands.
- It documents expected return conventions: zero success, negative communication/protocol errors, and positive MI status errors.
- It notes that Admin `_args` fd/timeout fields are ignored for MI, though implementation supports passthrough command timeout override on the endpoint.
