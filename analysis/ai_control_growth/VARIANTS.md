# Protocol variant coverage

The inventory distinguishes individual mechanisms and material operating points from entire parameter sweeps. Qualitative and conceptual entries are retained without invented safety measurements.

| Source | Indexed variants / families | With numerical evidence | Observations / bounds |
| --- | ---: | ---: | ---: |
| [AI Control](https://arxiv.org/html/2312.06942) | 21 | 20 | 29 |
| [Ctrl-Z](https://arxiv.org/html/2504.10374) | 12 | 9 | 19 |
| [Adaptive attacks on trusted monitors](https://arxiv.org/html/2510.09462) | 13 | 9 | 25 |
| [Evaluating control protocols for untrusted AI agents](https://arxiv.org/html/2511.02997) | 17 | 14 | 25 |
| [LinuxArena](https://arxiv.org/html/2604.15384) | 29 | 18 | 70 |
| [Retrying vs resampling](https://arxiv.org/html/2605.26047) | 79 | 71 | 71 |
| [Attack selection](https://arxiv.org/html/2606.06529) | 6 | 2 | 24 |
| [Bootstrapped monitoring](https://arxiv.org/html/2606.11998) | 8 | 7 | 152 |
| [Red-teaming Auto Mode](https://arxiv.org/html/2609.19587v2) | 12 | 5 | 42 |
| [MonitoringBench](https://arxiv.org/html/2605.09684) | 5 | 5 | 107 |
| [EvasionBench](https://arxiv.org/html/2609.30217) | 8 | 5 | 31 |
| [When can we trust untrusted monitoring?](https://arxiv.org/html/2602.20628) | 6 | 6 | 54 |
| [Scaling laws for scalable oversight](https://arxiv.org/html/2504.18530) | 6 | 0 | 0 |
| [Practical challenges of control monitoring](https://arxiv.org/html/2512.22154) | 4 | 0 | 0 |
| [OpenAI auto-review](https://alignment.openai.com/auto-review/) | 1 | 1 | 1 |

The fitted comparison has 160 defender candidates. Attacker-only ablations remain numerical evidence and are not credited as additional defenses.

The full per-variant ledger is [variant_inventory.json](variant_inventory.json). Numerical observations are in [evidence.json](evidence.json). Model code pools helper configurations; helper names, capabilities, honesty labels, and collusion-prompt grouping are not fit inputs. Architectures such as reasoning-only, actions, stateful monitoring, and summarized reasoning can differ.

Quoted figure readout intervals express extraction uncertainty, not sampling confidence intervals. Shared effects and transport uncertainty address dependence and missing capability placements; these adjustments do not validate comparisons at equal latency, usefulness or inference cost.
