-This requires NPM. You need to install Node.JS.
-This project was inspired by @pimanrules on YouTube's "Pokemon AI Tournament" video, particularly the AI explanation.

Avatars for bots can be found here: https://play.pokemonshowdown.com/sprites/trainers/

AI Personality Chunks:

1. Random (Implemented)
    Always picks an option at random
    
2. Knowledgeable: (Implemented)
    Knows the type matchup, gives slight priority to super effective attack
    .
3. Cautious: (Implemented)
    If their pokemon is at less than 1/3rd HP and they have a pokemon that is above that threshold, they'll prioritize switching, keeping in mind the type chart

4. Aggressive: (Implemented)
    Slightly prioritizes damaging moves.

5. Worrywart: (Implemented)
    Dramatically prioritizes healing moves upon low health, if available.

6. Stupid (Implemented)
    Doesn't follow safeguards, such as not applying statuses to already statused pokemon.

7. Opportunistic
    Prioritizes priority moves if the opponent is low on health.

8. Varied
    Adds slight randomness to choices.

9. Setup