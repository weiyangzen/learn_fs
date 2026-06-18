# sources/distributed-fs/tahoe-lafs/misc/operations_helpers/provisioning/web_reliability.py

## Purpose

This Nevow page wraps `ReliabilityModel` in a web form and renders simulation results.

## Important APIs, Types, and Functions

`get_arg` reads query args and form fields through `IRequest`. `is_available` reports whether the imported reliability module is present. `yandm` formats seconds into years/months. `ReliabilityTool` defines `DEFAULT_PARAMETERS`, `parse_time`, `format_time`, `get_parameters`, `renderHTTP`, `make_input`, `render_forms`, `data_simulation_table`, and renderers for rows and summary values.

## Control Flow

On each HTTP render, it parses parameters from the request, runs `ReliabilityModel.run`, stores parameters/results on `self`, and delegates to Nevow rendering. Form rendering echoes parameter inputs. Data/render methods fill slots from `self.results.samples`, especially the last row for summary loss and repair metrics.

## State, Dependencies, Integration, Risks, and Tests

State is stored on the page instance per request, which can be risky if shared across concurrent requests. Dependencies are Nevow, NumPy-backed reliability, and templates. Integration is `run.py` and `reliability.xhtml`. Risks include division by zero when cumulative repairs are zero, Python 2 division in time formatting, unvalidated parameters, and concurrency leakage through instance attributes. Tests should exercise `parse_time`/`format_time`, default parameter parsing, render methods with synthetic reports, and zero-repair cases.
