# sources/test-tools/kdevops/scripts/vllm-status-summary.py

## Purpose
Parses verbose vLLM status output, typically Ansible output, into a concise deployment summary with per-node state, images, Helm values, services, and suggested test commands.

## Important APIs
`parse_status_output(lines)` builds a status dictionary with timestamp, `ansible_running`, `nodes`, `overall_state`, `docker_images`, `helm_values`, and `services`. `print_simplified_status(status)` renders the summary. `main()` reads stdin and prints the report.

## Control flow
Parsing tracks the current section from marker lines such as `--- Kubernetes Pods ---` and tracks current node from Ansible result headers. It detects Helm deploy commands, Kubernetes readiness, minikube containers, 9P mirror mounts, pod states, Docker images, Helm image/model values, and Kubernetes services. Overall state is derived as deploying, configuring, running, starting, or stopped.

## State and dependencies
No persistence. Uses `datetime`, `re`, and stdin. Output includes Unicode symbols and human-oriented command snippets.

## Integration points
Designed behind a `make vllm-status-simplified` style target that pipes verbose status into this script.

## Risks and test signals
Parsing is tightly coupled to exact section headings and text patterns. Helm value parsing stores `_pending_repo` internally and may mis-associate tags if values are nested differently. Test with captured status logs for stopped, starting, deploying, and running deployments.
