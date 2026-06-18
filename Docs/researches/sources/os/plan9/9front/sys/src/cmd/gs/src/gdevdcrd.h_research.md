# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdcrd.h

Small public header for the sample device CRD helper.

Key contents:
- Include guard `gdevdcrd_INCLUDED`.
- Prototype:
  `int sample_device_crd_get_params(gx_device *pdev, gs_param_list *plist, const char *crd_param_name);`

Research notes:
- Depends on the including compilation unit already having declarations for `gx_device` and `gs_param_list`.
- This header is only an interface shim for `gdevdcrd.c`.
