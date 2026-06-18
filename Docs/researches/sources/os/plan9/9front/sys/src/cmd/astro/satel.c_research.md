# File Research: sources/os/plan9/9front/sys/src/cmd/astro/satel.c

Artificial satellite pass prediction support.

Important behavior:
- `satels` iterates configured satellite element files in `satlst`, parses element values, and samples passes during dark periods.
- `satel` computes a satellite’s position/elevation from orbital timing, inclination, eccentricity, rotation, and observer geometry.
- `vis` checks sunlight/visibility geometry.
- Generates event records for visible passes, marking significant named passes when configured.

`satlst` is empty in this source, so behavior depends on adding paths to that list.
