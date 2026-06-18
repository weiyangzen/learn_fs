# sources/test-tools/kdevops/terraform/lambdalabs/SET_API_KEY.sh

Purpose: operator-facing shell helper that prints instructions for configuring Lambda Labs API credentials. It does not mutate files; it only emits setup guidance.

There are no functions or complex APIs. The script prints a prominent warning, points users to `https://cloud.lambdalabs.com`, and instructs them to create `~/.lambdalabs/credentials` with mode `600`, then run `make bringup`.

Control flow is linear `echo` output. There is no persistence performed by the script, but the documented state is a credentials file in the user home directory. Integration points are any Terraform external data source or provider configuration that later reads `~/.lambdalabs/credentials`.

Risks include format mismatch with `extract_api_key.py`: this helper suggests writing only the raw API key, while the Python extractor expects INI-style sections containing `lambdalabs_api_key`. That inconsistency can cause setup failures. Test signals should execute the script and compare its instructions against the actual parser contract, then add an integration fixture for accepted credential formats.
