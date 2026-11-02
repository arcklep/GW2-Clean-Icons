GW2 Flat Icon Pack
==================

Every Guild Wars 2 skill icon from the official API (4,717 skills, 2,169 icons), cleaned up in the
spirit of WoW's CleanIcons:

- the ragged, hand-painted black frame cut off
- AI upscaled (Real-ESRGAN) to remove the blur of older 64 px art, then scaled to 128 x 128
- lightly sharpened
- one consistent flat style: rounded corners, no border (PNG with transparent corners)

Contents
--------

icons/        <skill name> - <file id>.png
              The name is the skill that most often uses the icon (many skills share one).
              The file id is the number at the end of the icon's render.guildwars2.com URL,
              so it matches the "icon" field of the GW2 API.
skills.csv    every skill: skill_id, skill_name, icon_file
skills.json   the same as a lookup: { "<skill id>": "<icon file>" } for addons and tools

Not included: condition and boon icons (Bleeding, Burning, Might, ...). The API's skill list does not
have them.

Credit and use
--------------

Guild Wars 2 icons (c) ArenaNet, LLC. All rights reserved. Cleaned and upscaled by joycat.

This is a free fan-made pack, shared under ArenaNet's Content Terms of Use. It is not made or endorsed
by ArenaNet. Use it freely in free addons, overlays and fan projects; do not sell it or use it
commercially. Please keep this README with the icons.
