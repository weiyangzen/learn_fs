# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdcrd.h

Header interface for the sample device CRD helper.

Key contents:
- Include guard `gdevdcrd_INCLUDED`.
- Declares `sample_device_crd_get_params(gx_device *pdev, gs_param_list *plist, const char *crd_param_name)`.

Role:
- Lets device implementations expose the sample CRD-building helper from `gdevdcrd.c` in their get-params path.

Dependencies:
- Requires `gx_device` and `gs_param_list` types to be visible to includers.

Notable risks:
- The header exposes only the helper declaration; all CRD behavior and limitations live in the C file.
