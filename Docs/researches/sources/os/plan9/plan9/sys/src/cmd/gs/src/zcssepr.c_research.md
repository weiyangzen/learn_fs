# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcssepr.c

Implements Separation color space support plus overprint state operators.

`.setseparationspace` expects a four-element color-space array and uses the current color space as the alternate space. It accepts separation names as strings or names, resolves special names `/All` and `/None`, validates the tint transform, builds a Separation color space, installs the tint function, and records interpreter references for layer name and tint transform.

The file notes that Separation is treated similarly to a single-component DeviceN color space except for `/All` and `/None`.

Overprint operators:
- `currentoverprint`
- `setoverprint`
- `.currentoverprintmode`
- `.setoverprintmode`

Memory handling frees the separation map on errors and decrements the map reference after successful installation.

Registered as Level 2 operators in `zcssepr_l2_op_defs`.
