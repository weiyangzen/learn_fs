# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/provisioning.py

## Purpose

This Nevow page implements a provisioning calculator for Tahoe grids. It estimates user data volume, shares, server storage, ownership/lease overhead, rates, costs, drive replacement load, availability, and repair-survival properties from form-selected parameters.

## Important APIs, Types, and Functions

`div_ceil`, `factorial`, and `binomial` provide math helpers. `ProvisioningTool` is a `rend.Page` with `docFactory` pointing at `provisioning.xhtml`. `render_forms` adapts Nevow requests to `do_forms`. `do_forms(getarg)` builds all input selectors and conditional output sections. `file_availability(k, n, server_dBA)` approximates file availability in dBA, and `many_files_availability(file_dBA, num_files)` approximates aggregate availability across many files.

## Control Flow

For non-POST or unfilled forms, it builds inputs with defaults. When `filled` is true, it computes file and space totals, erasure expansion, per-server buckets/shares, share metadata overheads, client/server operation rates, drive/server cost estimates, drive failure rates, dBA availability, and worst-case check-interval survival. It returns a Nevow form assembled from generated sections and optionally links to the reliability page if importable.

## State, Dependencies, Integration, Risks, and Tests

State is request-local except for template loading. Dependencies are Nevow, local `util.sibling`, and math. Integration is `run.py`, `test_provisioning.py`, and the XHTML template. Risks include Python 2 division in `div_ceil`, many hard-coded historical constants/costs, approximation validity only for high availability, branchy form code with little validation, and hidden assumptions about 3-of-10 overhead sizes. Tests should cover default rendering, filled rendering for wraparound and ownership modes, binomial math, invalid encoding strings, and availability monotonicity.
