# GW2 Clean Icons

Every Guild Wars 2 skill icon, plus boons, conditions and other effects, cleaned up for addons:
**2,740 icons** covering **5,642 skills** and **427 effects**, 128 × 128 PNG.

- **Skill icons:** the ragged, hand-painted black frame cut off; one flat style with rounded corners
  and no border.
- **Boons, conditions and other effects:** their own shape and border kept, with transparent edges.
  The small flat symbols (boons, conditions) use Real-ESRGAN's line-art model, which keeps their thin
  outlines even, with only a light touch of grit.
- **All icons:** AI upscaled (Real-ESRGAN) to remove the blur of the smaller and older art, then the
  originals' fine grain and brush texture laid back on top, so they keep the artists' gritty look
  instead of a smooth "AI" look.

## Downloads

From [Releases](../../releases):

- `GW2-Clean-Icons.zip`: the pack as addons use it (this repository's layout).
- `GW2-Clean-Icons-named.zip`: the same icons named for people (`skills/Fireball - 102965.png`,
  `effects/Might - 102852.png`), for browsing or your own projects.

## Layout

| Path | What it is |
|---|---|
| `icons/<file id>.png` | every icon. The file id is the number at the end of the icon's `render.guildwars2.com` URL, so it matches the `icon` field of the GW2 API. |
| `icons_square/<file id>.png` | the same icons with square corners instead of rounded ones (icons with their own shape, like boons and conditions, are identical in both) |
| `skills.json` | skill id → file id. Besides the API's skills, this covers the ids arcdps reports damage under that the API doesn't have (trait procs, pets, relics, siege, mounts, extra hits of a skill), mapped with [Elite Insights](https://github.com/baaron4/GW2-Elite-Insights-Parser)' icon table. Their art that isn't on `render.guildwars2.com` (from the wiki) has file ids from 900000000 up. |
| `effects.json` | effect name (as the API's skill and trait facts name it, e.g. `"Might"`, `"Poisoned"`) → file id |
| `effect_ids.json` | effect id as arcdps and buff lists use it → file id, for the core boons and conditions (the API has no effect ids) |
| `skills.csv`, `effects.csv` | the same with names, for people |
| `manifest.json` | name, version, counts |

## For addon developers

**Shared install location:** extract `GW2-Clean-Icons.zip` into Nexus' shared folder, so every addon
finds the same copy:

```
<Guild Wars 2>\addons\common\GW2-Clean-Icons\
```

In a Nexus addon that's `Paths_GetCommonDirectory()` + `\GW2-Clean-Icons\`. If `manifest.json` is
there, the pack is installed. Its `version` tells you which one.

**Looking up an icon:**
- From an icon URL you already have from the API: take the number before `.png` and load
  `icons/<that number>.png`.
- From a skill id: `skills.json[skill id]` gives the file id.
- From a boon or condition: `effect_ids.json[effect id]` or `effects.json[name]`.
- **Fallback:** if the file isn't there (new skills after a game patch, or the pack isn't installed),
  use the game's or the API's own icon.

**Fetching single icons** without installing the pack, through jsDelivr (pin a version):

```
https://cdn.jsdelivr.net/gh/arcklep/GW2-Clean-Icons@v1.1.0/icons/102965.png
```

Not included: icons the API doesn't serve (UI artwork, map markers).

## Credit and use

Guild Wars 2 icons © ArenaNet, LLC. All rights reserved. Cleaned and upscaled by joycat.

This is a free fan-made pack, shared under ArenaNet's Content Terms of Use. It is not made or endorsed
by ArenaNet. Use it freely in free addons, overlays and fan projects; do not sell it or use it
commercially. Please keep this README with the icons.
