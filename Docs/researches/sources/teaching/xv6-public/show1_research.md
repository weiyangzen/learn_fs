# File Research: sources/teaching/xv6-public/show1

Shell helper for previewing one formatted xv6 source listing.

Behavior:
- Runs `runoff1`, pipes through `pr.pl`, formats with `mpage`, writes `x.ps`, and opens it with `gv --swap`.
- Uses LucidaSans-Typewriter font parameters.

Role:
- Developer documentation preview script.
