# Development Journal — Mara's Siege
A chronological log of key developments, decisions and learnings throughout this project.

---

## 2026-10-21 — Rescued Mara's Siege from v24 and shipped v1.0

**Type:** Milestone

**TL;DR:** v24 was broken beyond patching. I rebuilt from the original, added features one at a time, and released v1.0 on itch.io.

**What I built or did**
> "Don't over do it like last time. Be satisfied."

v24 crashed on every map, and no v22 or v23 code had survived. I rebuilt from the original and added, one at a time: selling, two bosses, a Temple Garden map with paths, sound, and wall upgrades. Then:
> "this is good i like it but can we save the previous version as an alternative game mode?"

**Why I did it this way**
For ideas carried over from v24, I asked:
> "Can we try see if it's worth doing each of these."

That cut the zoomed maps and the pathfinding, which were the parts that broke v24.

**What I learned**
> "is it worth publishing when there is still potentially more development and improvements to come?"

Yes. Release early as "In development" and keep updating. Checking the README against the code also turned up three features that had never worked.

**How we did it**
1. Ran v24 on every map in test mode. It crashed every time.
2. Rebuilt from the original in one clean folder, testing after each feature.
3. Set up a public repo, rewrote the README and fixed the three broken features.
4. Built a `.exe`, published it on itch.io, then downloaded it back to check it.
5. Did an engineering pass: tests, config cleanup, a rename and a working screen shake.

**Engineering Contribution**
- *Decisions made:*
  - Rebuilt rather than patched v24. The crash was a symptom: v24's temple-breach code sat in the wrong loop.
  - Chose the temple garden theme over "pink Brian matter", because it fits the existing lotus, Buddha and monk art.
  - Level 3 walls fully block enemies instead of rerouting them. Rerouting needs pathfinding, the system that broke v24.
  - Made the dead screen-shake code work instead of deleting it.
  - Answered "Yes" honestly on itch.io's AI disclosure.
- *Improvements made to generated code:*
  - Removed 12 lines of duplicate and dead settings. `WALL_COLOR` was defined twice, and the second copy silently won.
  - Renamed `try_upgrade_tower` to `try_upgrade_selected`.
  - Fixed the shake, which was calculated then thrown away. It's now clipped to the map so the side panel stays readable.
  - Pinned `requirements.txt` and added the first test suite: 14 tests.
- *Accepted as-is vs engineered on:* Most code was AI-generated and accepted after test runs. My part was direction and scope: what to keep, cut, question and test by playing. The engineering pass reworked the config, naming and shake.
