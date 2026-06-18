# sources/test-tools/kdevops/scripts/vllm-quick-test.sh

## Purpose
Runs a quick functional test against kdevops vLLM deployments, covering baseline and optional development nodes.

## Important APIs
`test_node(node, node_type)` resolves node IP with Ansible, starts a kubectl port-forward for Kubernetes deployments when needed, calls the OpenAI-compatible completions endpoint, validates JSON, extracts completion text, and prints timing and response details.

## Control flow
The script loads `.config` and `extra_vars.yaml`, detects A/B mode, declared-host mode, and bare-metal vLLM mode, builds a `NODES` array, then tests each node. Requests are sent over SSH to `localhost:8000/v1/completions` with model `facebook/opt-125m`, prompt `kdevops is`, and max tokens 30.

## State and persistence
It may start background `kubectl port-forward` processes on target nodes and writes `/tmp/pf.log` remotely. It does not clean them up.

## Dependencies and integration
Requires `ansible`, `ssh`, `kubectl` on target for Kubernetes mode, `curl`, `bc`, and Python JSON tooling.

## Risks and test signals
Service naming is hard-coded as `vllm-prod-${node}-router-service`, which must match Helm output. JSON payload is shell-embedded and only safe for the fixed prompt. Success requires valid JSON, no API error message, and extractable choice text for every node.
