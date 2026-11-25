# DIGED News : procédure de production d'un Short

Positionnement : **« The world is changing. Understand why. »** Public : Américains (et Canadiens), anglais simple.
Un Short = une histoire, 40 à 50 secondes, compréhensible par quelqu'un qui scrolle.

## 0. Règles non négociables
- **Ne jamais inventer.** Chaque fait vient d'au moins 2 sources lisibles (ou 1 source officielle citée par un grand média). Une affirmation d'une seule partie (« Iran says… ») est attribuée ou écartée.
- **Test « pour toi »** : le sujet doit répondre en une phrase à « qu'est-ce que ça change pour un Américain : son argent, son travail, sa sécurité, sa soirée ? ». Sinon, on ne le fait pas.
- **Simple** : une idée par phrase, chiffres ronds, pas de jargon (quota, tarif, OMC…) sans image simple pour l'expliquer.
- Analyse ≠ fait : une conséquence possible s'écrit au conditionnel (« could »).
- Images : uniquement libres de droits (Pixabay, domaine public US) ou générées par nous. Jamais de photo d'agence (AP, Reuters, Getty).
- Le propriétaire publie lui-même pour l'instant : livrer la vidéo + titre + description + hashtags + tags + commentaire épinglé.

## 1. Choisir le sujet
`/usr/bin/python3 pipeline/detect.py` : 3 rayons (tendances Google US, sport, monde/économie).
Mix quotidien visé : 1-2 monde/géopolitique/économie, 1 sport, 1 tendance. Préférer ce qui a < 6 h et monte.

## 2. Vérifier
Lire les articles (curl ; Guardian/DW/CNBC/Benzinga bloquent → passer par WebSearch ou d'autres médias). Noter chaque fait avec sa source.

## 3. Script (≈ 130-150 mots)
Structure : ACCROCHE (0-3 s, parle au spectateur) → CE QUI SE PASSE → POURQUOI → CE QUE ÇA CHANGE POUR TOI → À RETENIR + « Follow DIGED News… ».
Écrire les nombres en toutes lettres pour la voix (« two hundred twenty-four thousand »).
Créer `shorts/<date>-<slug>/script.txt`.

## 4. Voix + sous-titres
```
/usr/bin/python3 pipeline/tts.py "$(cat shorts/X/script.txt)" en-US-AndrewNeural shorts/X/vo.mp3 "+0%"
/usr/bin/python3 pipeline/align.py shorts/X
```
Corriger dans caps.json les mots mal écrits (le texte affiché doit être celui du script).

## 5. Habillage
Copier `templates/overlay.html` → `shorts/X/ov.html`, remplir __HEADLINE__ (≤ 6 mots, accrocheur), __TAG__ (EXPLAINED / TRENDING / SPORTS / BREAKING), __SOURCES__, et écrire `scene(t)` en suivant les temps de caps.json (exemples dans `examples/`). Icônes, compteurs, schémas simples ; jamais de graphique chargé.
Aperçu : `node pipeline/ovshot.cjs <img> <img+1> 30 prev shorts/X` puis vérifier l'image.

## 6. Fonds vidéo
API Pixabay vidéos (clé : /tmp/claude-0/pixabay_key, ne jamais l'afficher). Télécharger dans `shorts/X/px/`. Un fond par partie. Écrire `shorts/X/short.json` :
`{"segments": [["shorts/X/px/v1.mp4", 0, 4.6], ...], "duration": 46.4, "output": "diged-<slug>.mp4"}`

## 7. Montage + contrôle
```
/usr/bin/python3 pipeline/build.py shorts/X
/usr/bin/python3 pipeline/check_voice.py shorts/X/diged-<slug>.mp4 shorts/X/script.txt
```
Exiger ≥ 97 % de mots retrouvés. Regarder 4 images du MP4 final (accroche, milieu, fin) avant de livrer.

## 8. Livrer
Envoyer la vidéo au propriétaire avec : titre (≤ 100 caractères, finit par #shorts), description (faits + sources + hashtags), tags YouTube, commentaire épinglé, meilleure heure (17h-20h Maroc = midi-15h New York). Ne pas committer les MP4 (voir .gitignore).

## Format « titre seul » 8 s en boucle (validé le 25/11/2026) — `pipeline/loop8.py`
Une seule page, tout visible du début à la fin, sans voix, musique « suspense » en boucle (`pipeline/music_loop.py`).
- `shorts/<date>-<slug>/spec.json` (voir l'en-tête de loop8.py) puis `/usr/bin/python3 pipeline/loop8.py shorts/<date>-<slug>`.
- **Images cohérentes avec le titre (règle du propriétaire)** : le fond montre littéralement les mots-clés du titre
  (explosion + armée US → vraie explosion + drapeau US ; un joueur → sport du joueur). Jamais un fond abstrait (fumée, couleurs).
  Enchaîner 2 clips (`"bg": [[clip, début, durée], ...]`, 8 s au total) : l'action forte au début de la boucle (sur le coup de musique).
  Interdits : guerre réelle d'un autre pays, nucléaire, ou toute image qui ferait croire à autre chose que l'info.
- Personne citée : petit médaillon rond (`"photo"`), photo libre (CC0 / domaine public US), crédit dans `credit`.
- Toujours regarder une planche de 4-5 images de la vidéo finale avant envoi.
- Fichier ≤ 5 Mo (Make gratuit) : loop8.py plafonne le débit.
