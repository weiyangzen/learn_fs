# sources/test-tools/strace/bundled/linux/include/uapi/linux/v4l2-common.h

Purpose: provides common Video4Linux2 selection and EDID definitions shared by main V4L2 and V4L2 subdevice APIs. The comment advises including it indirectly through `videodev2.h` or `v4l2-subdev.h`, but the header carries reusable ABI constants.

Important APIs/types/functions: selection target constants describe crop and compose rectangles: `V4L2_SEL_TGT_CROP`, `CROP_DEFAULT`, `CROP_BOUNDS`, `NATIVE_SIZE`, `COMPOSE`, `COMPOSE_DEFAULT`, `COMPOSE_BOUNDS`, and `COMPOSE_PADDED`. Selection flags are `V4L2_SEL_FLAG_GE`, `V4L2_SEL_FLAG_LE`, and `V4L2_SEL_FLAG_KEEP_CONFIG`. `struct v4l2_edid` contains `pad`, `start_block`, `blocks`, five reserved `__u32` fields, and a user pointer `__u8 *edid`. Backward-compatibility aliases map older crop/compose target and subdevice flag names to the common constants.

Control flow: none locally. Drivers and applications use the constants in V4L2 selection ioctls to request current/default/bounds/native rectangles and use `struct v4l2_edid` to read or write EDID block ranges through video device ioctls.

State/persistence behavior: selection values are runtime device or subdevice configuration, and `KEEP_CONFIG` asks the driver not to reconfigure dependent settings while satisfying a requested rectangle constraint. EDID data is transferred through the pointer provided in `v4l2_edid`; reserved fields are ABI padding and should remain zeroed by callers.

Dependencies/integration: depends on `linux/types.h`. It is integrated by V4L2 core headers and must stay source-compatible with both video-node and subdevice users. strace should decode selection target and flag values wherever V4L2 selection or subdevice selection structs appear, and decode `v4l2_edid` pointer/block metadata when handling EDID ioctls.

Risks and test signals: risks are alias drift, mixing crop and compose target ranges, and unsafe decoding of the user pointer inside `struct v4l2_edid`. Tests should cover each target name, flag combinations, old alias names, EDID block count/start values, null and non-null EDID pointers, and reserved fields.
