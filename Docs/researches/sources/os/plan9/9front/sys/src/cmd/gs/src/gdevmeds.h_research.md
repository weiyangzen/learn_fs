# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmeds.h

## Role

Small public interface for medium selection support implemented elsewhere in `gdevmeds.c`.

## Key API

- Includes `gdevprn.h`, so it is tied to Ghostscript printer devices.
- Declares `int select_medium(gx_device_printer *pdev, const char **available, int default_index);`.
- The function is expected to choose a printer medium from an available-medium list, falling back to `default_index`.

## Dependencies and Context

This header does not implement logic. It is an integration point for printer drivers that need media selection based on a `gx_device_printer`.

## Research Notes

No filesystem logic. The only operational relevance is that printer devices may select output media before page emission.
