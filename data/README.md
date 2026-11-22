# Data

All three datasets record the 20×20 Black Box grid (`BlackBox_N.php`, numerical version) after **every single step**. Each value is the cell's number, 0-9; Area 3 occasionally shows 10-13.

| Folder | Source | Contents | Role |
|---|---|---|---|
| `group1_runs/` | SSIE 501 Group 1, scraper notebook (`requests` + `BeautifulSoup`) | `run_00.npy` … `run_60.npy`; each array is (2001, 20, 20): the Reset grid, then 2,000 single steps | **Discovery**: rules are found here |
| `shared_dataset/` | Shared dataset compiled by W. Zhang (Selenium controller) | `trajectory_001_FULLBOX.npz` … `trajectory_030_FULLBOX.npz`; key `full_history` (2000, 20, 20), `recorded_steps` 1…2000 | **Held-out**: rules are only tested here |
| `group2/` | SSIE 501 Group 2, `blackbox_collect.py` | `frames.csv`: one row per step (`step`, then 400 cell values in row-major order) | Small extra check |
| `group5_runs/` | Group 5, `collect/recorder.js`, 16 November 2026 | `blackbox_single_01_20261116.json` … `_10_`: Reset grid then 2,000 single steps; `blackbox_tenstep_01/02_20261116.json`: 200 presses of Next 10 Steps. Each file holds the Reset grid, the cells changed at each press, the page's step counter after each press and the final grid | **Fresh test data (F)**, recorded after the rules were written down |

**Included in this repository:** `shared_dataset/` (the held-out runs, posted for the class by the instructor) and `group5_runs/` (our own recordings) and `marcus_recordings/` (the recordings the Region 1, 2 and 4 rules were found on; see its README).
**Not included yet:** `group1_runs/` and `group2/`. Every script loads the discovery runs, so `run_all.py` needs them in place first.

To get the missing files, ask the course group that shared them, or recollect them with any of the scrapers above, and place them in these folders with these names. `blackbox/data.py` checks that the frames are consecutive single steps.
