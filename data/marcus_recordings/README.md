# Marcus Washington's recordings

These are the recordings the Region 1, 2 and 4 rules were found on ("Marcus's recordings, 32 runs + 200 short runs" on slide 4 of the Part 2 presentation). They are separate from the datasets the rules were tested on (D, H, G2 and F).

Every file holds the 20×20 grid of the numerical Black Box page, read from the rendered cell colours, starting at the Reset grid.

| File | Contents | Recorded |
|---|---|---|
| `september_single_step_runs.npz` | 32 runs, one array per run of shape (steps + 1, 20, 20). Frame 0 is the Reset grid and each frame after it is one step later. 21,720 steps in total: 20 runs of 36 steps, 2 of 500, 5 of 1,000 and 5 of 3,000. | 23-24 September 2026 |
| `october_short_runs.npz` | 200 runs of 50 steps. `grids` has shape (200, 51, 20, 20); `run_id` names each run. 10,000 steps in total. | 21 October 2026 |
| `september_ten_step_runs.npz` | 5 runs recorded with "Next 10 Steps": 300 presses each, so consecutive frames are 10 steps apart. Not used to find the rules; included for completeness. | 24 September 2026 |
| `runs.json` | One row per September run: who collected it, steps per press, number of presses, unreadable cells. | |

Values are 0-9. A value of -1 marks a cell whose colour was not one of the ten digit colours. These only occur in Region 3, where the page shows values 10-13.

Row 0 is the top row and column 0 is the left column, the same layout as the other datasets in `data/`.

## How they were collected

Marcus Washington set up and ran the collection. The clicking and reading were done by AI agents driving a browser, each reading only the cell colours and the page's step counter:

| Runs | Agent |
|---|---|
| `C_*` (11 runs) | Claude in Cowork |
| `H_S*`, `H_L01` (11 runs) | Hermes agent running GLM 5.3 |
| `G_M*` (5 runs), `G_N*` (5 ten-step runs) | HyperAgent, GPT-6 Astra foreman |
| `H_K*` (5 runs) | Hermes agent running GLM 5.3 |
| October short runs (200) | Claude Haiku in Cowork |

Each run used its own browser session, the page counter was checked after every press, and each grid was read twice.

Only the grids are included here. The raw captures (about 750 MB unpacked, including copies of the page itself) are kept by Marcus and are available on request.

## Loading

```python
import numpy as np
runs = np.load("data/marcus_recordings/september_single_step_runs.npz")
grids = runs["G_M01"]          # (3001, 20, 20)
short = np.load("data/marcus_recordings/october_short_runs.npz")["grids"]   # (200, 51, 20, 20)
```

## Check

`blackbox.rule_checks.evaluate` on these recordings (21 November 2026):

| | 32 September runs | 200 October runs |
|---|---|---|
| Region 1 changes from 0-3 or 6-9, gates right | 6,158 of 6,158 | 7,867 of 7,867 |
| Region 2 minimum part | 1,106 of 1,106 | 2,250 of 2,250 |
| Region 2 multiply part | 1,299 of 1,299 | 3,544 of 3,544 |
| Region 4 swaps, strict rule in update order | 902 of 902 | 2,354 of 2,354 |
