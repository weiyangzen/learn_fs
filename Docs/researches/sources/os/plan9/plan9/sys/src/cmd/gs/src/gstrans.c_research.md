# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.c

## Purpose
Implements non-rendering transparency state management and PDF 1.4 compositor request packaging. It updates graphics-state transparency fields, begins/ends groups and masks, samples transfer functions, and forwards imager-level transparency operations to device procedures.

## Public Surface
- State setters/getters: `gs_setblendmode`, `gs_currentblendmode`, `gs_setopacityalpha`, `gs_currentopacityalpha`, `gs_setshapealpha`, `gs_currentshapealpha`, `gs_settextknockout`, `gs_currenttextknockout`.
- Stack query: `gs_current_transparency_type`.
- Group APIs: `gs_trans_group_params_init`, `gs_begin_transparency_group`, `gx_begin_transparency_group`, `gs_end_transparency_group`, `gx_end_transparency_group`.
- Mask APIs: `gs_trans_mask_params_init`, `gs_begin_transparency_mask`, `gx_begin_transparency_mask`, `gs_end_transparency_mask`, `gx_end_transparency_mask`, `gs_init_transparency_mask`, `gx_init_transparency_mask`.
- Device push/pop: `gs_push_pdf14trans_device`, `gs_pop_pdf14trans_device`.
- Layer discard stub: `gs_discard_transparency_layer`.

## Control Flow
- Setters clamp alpha values to `[0,1]`, range-check blend mode, and update fields in `gs_state`.
- `gs_state_update_pdf14trans` calls `send_pdf14trans` with `gs_pdf14trans_params_t`; if a new compositor device is returned, it installs it in the graphics state.
- `gs_begin_transparency_group` fills PDF14 params with group isolation/knockout, current opacity/shape/blend mode, and BBox, then sends `PDF14_BEGIN_TRANS_GROUP`.
- `gx_begin_transparency_group` is the imager-side counterpart; it validates background component count, copies opacity/shape/blend mode into `pis`, and calls the device `begin_transparency_group` proc if present.
- Mask begin initializes PDF14 params, copies background arrays, detects identity transfer function, samples the transfer function into 256 bytes, and sends `PDF14_BEGIN_TRANS_MASK`.
- `gx_begin_transparency_mask` converts PDF14 params into `gx_transparency_mask_params_t` and calls the device proc if available.
- Mask init clears the selected opacity/shape mask reference in the imager state.
- Push/pop device APIs send PDF14 push/pop opcodes without other parameters.

## Internal Stack Code
- A simple `gs_transparency_state_t` descriptor is defined.
- `PUSH_TS` is `0`, so `push_transparency_stack` is compiled out.
- `pop_transparency_stack` frees the current transparency stack node. `gs_discard_transparency_layer` calls this but is marked `NYI, DUMMY`; without stack pushes in this file, it only works if another path populated `pgs->transparency_stack`.

## Dependencies
Uses `gstrans.h`, graphics state internals, devices, and PDF14 compositor support from `gdevp14.h`.

## Risks and Notes
- Group color space is currently not used for blending; comments say blending color space is based on the process color model of the output device.
- Transfer-function sampling ignores callback return codes; the code calls `TransferFunction` and converts `out` directly.
- `gs_discard_transparency_layer` is explicitly incomplete/dummy.
