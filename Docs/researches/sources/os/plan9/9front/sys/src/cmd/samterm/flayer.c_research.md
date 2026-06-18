# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/flayer.c

`flayer.c` implements samterm's overlapping text-window layer abstraction on top of `Frame`.

It maintains a front-to-back `Flayer` list, visibility classification (`None`, `Some`, `All`), per-layer backing images for partially covered windows, and separate color palettes for command and main text windows.

`flnew`, `flinit`, `flclose`, `flupfront`, `llinsert`, and `lldelete` manage layer lifetime and stacking. `newvisibilities`, `visibility`, and `flrefresh` compute obscured regions and repaint visible fragments.

`flrect`, `flresize`, and `rscale` manage layer geometry, scroll-bar area, and screen-resize scaling. Resize clears/rebuilds frames and enforces minimum window dimensions.

`flinsert`, `fldelete`, `flsetselect`, and `flfp0p1` synchronize visible frame text and selection with global file offsets. Repainting is optimized by only drawing changed selection spans where possible.

`flselect` brings a layer forward, detects double/triple clicks by time/distance, updates global `sel`, and delegates drag selection to the frame library.

`flprepare` lazily reconstructs a layer frame/backing image when it becomes visible, reloads text through the layer's `textfn`, redraws selection, and redraws scroll state.
