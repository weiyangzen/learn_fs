# sources/user-network-fs/rclone/bin/test_metadata_mapper.py

Purpose: sample metadata mapper for rclone metadata migration workflows. It reads JSON from stdin, modifies the `Metadata` object by appending a migration tag to `description` and replacing `domain1.com` with `domain2.com` in `owner`, then writes JSON to stdout.

State is pure stdin/stdout transformation. Dependencies are Python JSON and expected input shape containing `Metadata`. Risks include KeyError on missing `Metadata`, simplistic owner replacement, and no schema validation. Test signal is manual invocation or use as a fixture/demo in metadata mapper tests.
